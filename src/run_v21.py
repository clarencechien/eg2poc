"""J extension on frozen v2 data, via the existing jevlike fixed decision interface."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import time
from pathlib import Path
import requests
from huggingface_hub import hf_hub_download
from .common import read_jsonl, write_jsonl, append_jsonl, digest
from .run_v2 import verify_data
from .j_arm import JArm


def key(lang,text,mode,old=None):
    return hashlib.sha256(json.dumps([lang,text,mode,old],ensure_ascii=False).encode()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model-size',choices=['e2b','e4b'],required=True)
    ap.add_argument('--output',default='results/synthetic-v2.1');ap.add_argument('--server',default='/workspace/llama.cpp/build/bin/llama-server');ap.add_argument('--jevlike',default='/workspace/jevlike');ap.add_argument('--port',type=int,default=8083)
    ap.add_argument('--probe-only',action='store_true');args=ap.parse_args()
    if json.loads(Path('results/synthetic-v2/manifest.json').read_text())['status']!='complete':raise ValueError('Finish v0.2 before J inference')
    verify_data(Path('data/synthetic-v2'));planroot=Path('data/synthetic-v2.1');frozen=json.loads((planroot/'manifest.json').read_text())
    for f,h in frozen['sha256'].items():
        if digest(planroot/f)!=h:raise ValueError('J plan changed after freeze')
    plan=json.loads((planroot/'analysis-plan.json').read_text());config=json.loads(Path('data/synthetic-v2/config.json').read_text())
    if digest('data/synthetic-v2/manifest.json')!=plan['data_manifest_sha256']:raise ValueError('J data provenance changed')
    rows=read_jsonl('data/synthetic-v2/pairs.jsonl');docs=read_jsonl('data/synthetic-v2/docsets.jsonl');rowmap={p['pair_id']:p for p in rows}
    scope=json.loads((planroot/'scoring-scope.json').read_text())
    active_ids=set(scope['pair_ids']);active_rows=[p for p in rows if p['pair_id'] in active_ids]
    out=Path(args.output)/args.model_size;out.mkdir(parents=True,exist_ok=True)
    model=plan['models'][args.model_size];path=hf_hub_download(model['model_id'],model['file'],revision=model['revision'],local_files_only=True)
    manifest={'plan_sha256':digest(planroot/'analysis-plan.json'),'scope_sha256':digest(planroot/'scoring-scope.json'),'model':model,'model_bytes':Path(path).stat().st_size,
              'jevlike_revision':plan['jevlike_revision'],'llama_cpp_revision':plan['llama_cpp_revision'],
              'source_sha256':{f:digest(f) for f in ('src/j_arm.py','src/run_v21.py')},'server_binary_sha256':digest(args.server),
              'model_sha256':digest(path),'device':'cpu','threads':4,'benchmark_cache_prompt':False,'scoring_cache_prompt':plan['execution_cache_prompt'],'status':'running',
              'packages':{p:importlib.metadata.version(p) for p in ('requests','urllib3','cmake','huggingface_hub')}}
    expected_blob=Path(path).resolve().name
    if len(expected_blob)==64 and all(c in '0123456789abcdef' for c in expected_blob):
        if manifest['model_sha256']!=expected_blob:raise ValueError('Model SHA256 differs from downloaded LFS blob identifier')
        manifest['model_lfs_sha256_verified']=True
    mp=out/'manifest.json'
    if mp.exists():
        previous=json.loads(mp.read_text())
        for k in ('plan_sha256','scope_sha256','model','jevlike_revision','source_sha256','server_binary_sha256','model_sha256'):
            if previous[k]!=manifest[k]:raise ValueError(f'Cannot resume changed J provenance: {k}')
    manifest['started_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    def save():mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    save()
    command=[args.server,'-m',path,'--host','127.0.0.1','--port',str(args.port),'-ngl','0','-t','4','-tb','4','-c','4096','-np','1','--swa-full','--no-webui','-b','512','-ub','512']
    manifest['server_command']=command;save()
    log=(out/'server.log').open('a');server=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
    url=f'http://127.0.0.1:{args.port}';session=requests.Session();session.trust_env=False;start=time.monotonic()
    try:
        for _ in range(240):
            if server.poll() is not None:raise RuntimeError('llama-server exited; see server.log')
            try:
                if session.get(url+'/health',timeout=2).status_code==200:break
            except requests.RequestException:pass
            time.sleep(1)
        else:raise TimeoutError('llama-server not ready within 240s')
        arm=JArm(plan,config,args.model_size,url,args.jevlike);manifest['label_ids']=arm.label_ids
        manifest['template_sha256']=hashlib.sha256(arm.renderer.template.encode()).hexdigest();save()
        cache_file=out/'predictions.jsonl';cached={r['key']:r for r in read_jsonl(cache_file)} if cache_file.exists() else {}
        def infer(text,lang,mode,old=None,allow_cache=True):
            k=key(lang,text,mode,old)
            if allow_cache and k in cached:return cached[k]
            r={'key':k,**arm.score_j(text,lang,mode,old,cache_prompt=plan['execution_cache_prompt'] if allow_cache else False)}
            if allow_cache:append_jsonl(cache_file,r);cached[k]=r
            return r
        warm=rowmap[plan['benchmark_pair_ids'][0]]
        warmup=infer(warm['new_text'],warm['lang'],'single',allow_cache=False)
        (out/'warmup.json').write_text(json.dumps(warmup,ensure_ascii=False,indent=2)+'\n')
        print(f"{args.model_size} warmup: {warmup['latency_ms']:.1f} ms, {warmup['prompt_tokens']} tokens, missing {warmup['missing']}",flush=True)
        if args.probe_only:
            manifest.update(status='probe_only',probe_seconds=time.monotonic()-start);save();return
        benchmark_file=out/'benchmark.jsonl';bench={r['pair_id']:r for r in read_jsonl(benchmark_file)} if benchmark_file.exists() else {}
        for i,pid in enumerate(plan['benchmark_pair_ids']):
            if pid not in bench:
                p=rowmap[pid];r={'pair_id':pid,**infer(p['new_text'],p['lang'],'single',allow_cache=False)}
                append_jsonl(benchmark_file,r);bench[pid]=r
                k=key(p['lang'],p['new_text'],'single');cached[k]={'key':k,**r};append_jsonl(cache_file,cached[k])
            if (i+1)%10==0:print(f'{args.model_size} benchmark {i+1}/100',flush=True)
        unique={key(p['lang'],p['new_text'],'single'):(p['lang'],p['new_text']) for p in active_rows}
        for i,(lang,text) in enumerate(unique.values()):
            infer(text,lang,'single')
            if (i+1)%20==0:print(f'{args.model_size} single {i+1}/{len(unique)}; wall {time.monotonic()-start:.0f}s',flush=True)
        for i,p in enumerate(active_rows):
            infer(p['new_text'],p['lang'],'paired',p['old_text'])
            if (i+1)%20==0:print(f'{args.model_size} paired {i+1}/{len(active_rows)}; wall {time.monotonic()-start:.0f}s',flush=True)
        scores=[]
        for p in rows:
            if p['pair_id'] not in active_ids:
                scores.append({'pair_id':p['pair_id'],f'J_{args.model_size}_single':None,f'J_{args.model_size}_paired':None,'status':'outside J protocol contrasts; T10 evaluated as concat'})
                continue
            single=infer(p['new_text'],p['lang'],'single');paired=infer(p['new_text'],p['lang'],'paired',p['old_text'])
            scores.append({'pair_id':p['pair_id'],f'J_{args.model_size}_single':single['score'],f'J_{args.model_size}_paired':paired['score'],
                           'single_prediction_key':single['key'],'paired_prediction_key':paired['key']})
        write_jsonl(out/'scores.jsonl',scores)
        docresults=[]
        for i,d in enumerate(docs):
            context='\n\n'.join(rowmap[pid]['new_text'] for pid in d['pair_ids']);r=infer(context,d['lang'],'docset')
            docresults.append({'docset_id':d['docset_id'],'matched_set_id':d['matched_set_id'],'lang':d['lang'],'label':d['label'],f'J_{args.model_size}_single':r['score'],'prediction_key':r['key']})
            if (i+1)%10==0:print(f'{args.model_size} docsets {i+1}/{len(docs)}',flush=True)
        write_jsonl(out/'docset-scores.jsonl',docresults)
        manifest.update(status='complete',n_pairs=len(scores),n_scored_pairs=len(active_rows),n_outside_scope=len(rows)-len(active_rows),n_docsets=len(docresults),unique_predictions=len(cached),
                        n_missing_single=sum(r[f'J_{args.model_size}_single'] is None for r in scores if r['pair_id'] in active_ids),
                        n_missing_paired=sum(r[f'J_{args.model_size}_paired'] is None for r in scores if r['pair_id'] in active_ids),last_session_seconds=time.monotonic()-start,
                        finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        manifest['output_sha256']={f:digest(out/f) for f in ('scores.jsonl','docset-scores.jsonl','benchmark.jsonl','predictions.jsonl')};save()
        print(json.dumps({k:manifest[k] for k in ('status','n_pairs','n_docsets','n_missing_single','n_missing_paired','last_session_seconds')},indent=2),flush=True)
    except BaseException as e:
        manifest.update(status='interrupted_or_failed',error=f'{type(e).__name__}: {e}');save();raise
    finally:
        server.terminate()
        try:server.wait(timeout=15)
        except subprocess.TimeoutExpired:server.kill();server.wait()
        log.close()

if __name__=='__main__':main()

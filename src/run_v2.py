"""Resume-safe CPU runner for frozen synthetic-v2; no Gemini/API calls."""
import argparse
import gc
import hashlib
import importlib.metadata
import json
import time
from pathlib import Path
import numpy as np
from .common import read_jsonl, write_jsonl, digest, append_jsonl
from .arms import EmbeddingArms, NLIArm, score_a, cosine_distance, score_d2, score_r, score_docset

SETS=('same','alt','xlang')
PREFIXES=('classification','search_query')


def task_key(premise, hypothesis):
    return hashlib.sha256(json.dumps([premise,hypothesis],ensure_ascii=False).encode()).hexdigest()


def verify_data(root):
    manifest=json.loads((root/'manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        if digest(root/name)!=expected: raise ValueError(f'Frozen input changed: {name}')
    return manifest


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',default='data/synthetic-v2');ap.add_argument('--output',default='results/synthetic-v2');args=ap.parse_args()
    data, out=Path(args.data),Path(args.output);inputs=verify_data(data)
    config=json.loads((data/'config.json').read_text());rows=read_jsonl(data/'pairs.jsonl');docs=read_jsonl(data/'docsets.jsonl')
    sources={f:digest(f) for f in ('src/arms.py','src/run_v2.py')}
    identity={'inputs':inputs['sha256'],'source_sha256':sources,'config':config}
    fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    out.mkdir(parents=True,exist_ok=True)
    manifest_path=out/'manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        if manifest['fingerprint']!=fingerprint:raise ValueError('Inputs or scoring source changed; use a new output directory')
    else:
        manifest={**identity,'fingerprint':fingerprint,'status':'running','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                  'packages':{p:importlib.metadata.version(p) for p in ('torch','torchvision','transformers','sentence-transformers','numpy','scikit-learn')},
                  'device':'cpu','dtype':'float32','threads':4,'gemini_calls':0,'D2_DM':'not run (optional; no verified local setup)',
                  'missing_value_policy':'null, never substituted with zero'}
    def save_manifest():manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    save_manifest()
    cache=Path('.cache/experiments')/fingerprint;cache.mkdir(parents=True,exist_ok=True)
    texts=sorted({p[k] for p in rows for k in ('old_text','new_text')})
    started=time.monotonic()
    import torch
    torch.set_num_threads(4)
    embed_file=cache/'embeddings.npz'
    embedding=EmbeddingArms(config['embedding'],config['labels_same'])
    if embed_file.exists():
        saved=np.load(embed_file)
        vectors=saved['documents']
        for labels_set in SETS:
            for lang in ('zh','en'):
                for prefix in PREFIXES:
                    embedding.labels[labels_set,lang,prefix]=saved[f'{labels_set}-{lang}-{prefix}']
        print('Restored frozen embedding cache',flush=True)
    else:
        print(f'Encoding {len(texts)} unique paragraphs',flush=True)
        vectors=embedding.encode(texts,config['embedding']['document_template'])
        saved={'documents':vectors}
        for labels_set in SETS:
            for lang in ('zh','en'):
                for prefix in PREFIXES:
                    labels=embedding.encode(config[f'labels_{labels_set}'][lang],config['embedding'][f'{prefix}_template'])
                    embedding.labels[labels_set,lang,prefix]=labels;saved[f'{labels_set}-{lang}-{prefix}']=labels
        np.savez_compressed(embed_file,**saved)
    embedding.cache=dict(zip(texts,vectors))
    if not (out/'determinism.json').exists():
        t0=[p for p in rows if p['category']=='T0']
        repeated=embedding.encode([p['old_text'] for p in t0],config['embedding']['document_template'])
        distances=[cosine_distance(embedding.cache[p['old_text']],v) for p,v in zip(t0,repeated)]
        (out/'determinism.json').write_text(json.dumps({'n':len(t0),'repeat_runs':1,'mean':float(np.mean(distances)),
            'p95':float(np.percentile(distances,95)),'max':max(distances),'distances':distances},indent=2)+'\n')
    results=[]
    for p in rows:
        r={'pair_id':p['pair_id'],'A':score_a(p['old_text'],p['new_text']),
           'B768':embedding.score_b(p['old_text'],p['new_text']),
           'R':score_r(p['old_text'],p['new_text'],p['lang'],config['date_regex']) if p['category'] in ('T4','T5') else None}
        for s in SETS:
            for prefix in PREFIXES:
                key=f'C_{s}_{prefix}'
                r[key],r[key+'_argmax']=embedding.score_c(p['old_text'],p['new_text'],p['lang'],prefix,s)
        results.append(r)
    write_jsonl(out/'embedding-scores.jsonl',results)
    del embedding;gc.collect()
    print('EG2 complete; loading NLI label projection model',flush=True)
    nli=NLIArm(config['nli'])
    manifest['nli_id2label']=nli.model.config.id2label
    manifest['embedding_parameters']='text-only, 768 dimensions; frozen document and label prefixes; temperature 0.045'
    save_manifest()
    tasks={}
    for p in rows:
        for premise,hypothesis in ((p['old_text'],p['new_text']),(p['new_text'],p['old_text'])):
            tasks[task_key(premise,hypothesis)]=(premise,hypothesis)
        for text in (p['old_text'],p['new_text']):
            for s in SETS:
                for label in config[f'labels_{s}'][p['lang']]:tasks[task_key(text,label)]=(text,label)
    cache_file=cache/'nli.jsonl'
    cached={r['key']:r['probs'] for r in read_jsonl(cache_file)} if cache_file.exists() else {}
    pending=[k for k in tasks if k not in cached]
    # Sort by token length to reduce padding. This changes no labels or thresholds.
    lengths=nli.tokenizer([tasks[k][0] for k in pending],[tasks[k][1] for k in pending],truncation=False,padding=False)['input_ids'] if pending else []
    lengthmap={k:len(ids) for k,ids in zip(pending,lengths)}
    if lengthmap and max(lengthmap.values())>512:raise ValueError('NLI context exceeds 512')
    pending.sort(key=lambda k:(lengthmap[k],k))
    batch=config['v2']['nli_batch_size']; t=time.monotonic()
    print(f'NLI unique tasks: {len(tasks)}; cached: {len(cached)}; pending: {len(pending)}; batch: {batch}',flush=True)
    for offset in range(0,len(pending),batch):
        keys=pending[offset:offset+batch];probs=nli.label_probabilities([tasks[k] for k in keys])
        with cache_file.open('a') as f:
            for k,v in zip(keys,probs):
                cached[k]=v;f.write(json.dumps({'key':k,'probs':v})+'\n')
            f.flush()
        if offset%(batch*10)==0 or offset+batch>=len(pending):
            done=min(offset+batch,len(pending));elapsed=time.monotonic()-t
            print(f'NLI {done}/{len(pending)} ({elapsed:.1f}s; estimated remaining {elapsed/max(done,1)*(len(pending)-done):.0f}s)',flush=True)
            (out/'progress.json').write_text(json.dumps({'stage':'NLI','complete':len(cached),'total':len(tasks),'elapsed_this_session_seconds':elapsed})+'\n')
    for p,r in zip(rows,results):
        r['D1']=max(cached[task_key(a,b)][nli.contradiction] for a,b in ((p['old_text'],p['new_text']),(p['new_text'],p['old_text'])))
        rule=score_r(p['old_text'],p['new_text'],p['lang'],config['date_regex'])
        for s in SETS:
            labels=config[f'labels_{s}'][p['lang']]
            old=[cached[task_key(p['old_text'],label)] for label in labels]
            new=[cached[task_key(p['new_text'],label)] for label in labels]
            d=score_d2(old,new,nli.entailment,nli.contradiction)
            for k,v in d.items():r[f'D2_{s}_{k}']=v
            r[f'final_{s}']=None
            if p['category'] in ('T4','T5') or (p['category'] in ('T6','T8','T3') and p['strength'] in ('word','sentence')):
                r[f'final_{s}']=d['single'] if rule is None else max(rule,d['single'])
    write_jsonl(out/'scores.jsonl',results)
    arms=[k for k in results[0] if (k.startswith('C_') and not k.endswith('_argmax')) or k.startswith('D2_') and not k.endswith('_argmax')]
    threshold={a:float(np.percentile([r[a] for p,r in zip(rows,results) if p['category']=='T3' and r[a] is not None],95)) for a in arms}
    scoremap={r['pair_id']:r for r in results}
    docresults=[]
    for doc in docs:
        d={'docset_id':doc['docset_id'],'matched_set_id':doc['matched_set_id'],'lang':doc['lang'],'label':doc['label']}
        for a in arms:
            scores=score_docset([scoremap[pid][a] for pid in doc['pair_ids']],threshold[a])
            for k,v in scores.items():d[f'{a}_{k}']=v
        docresults.append(d)
    write_jsonl(out/'docset-scores.jsonl',docresults)
    (out/'docset-thresholds.json').write_text(json.dumps(threshold,indent=2)+'\n')
    manifest.update(status='complete',n_pairs=len(rows),n_docsets=len(docs),unique_texts=len(texts),nli_unique_tasks=len(tasks),
                    finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),last_session_seconds=time.monotonic()-started)
    manifest['output_sha256']={f:digest(out/f) for f in ('scores.jsonl','docset-scores.jsonl','determinism.json')}
    save_manifest();print(json.dumps({k:manifest[k] for k in ('status','n_pairs','n_docsets','unique_texts','nli_unique_tasks','last_session_seconds')},indent=2),flush=True)

if __name__=='__main__':main()

"""Reproduce J infrastructure checks on two fixtures, separate from corpus evaluation."""
import argparse
import json
import subprocess
import time
from pathlib import Path
import requests
from huggingface_hub import hf_hub_download
from .j_arm import JArm

FIXTURES=[('en','A demonstration project is proceeding on schedule. The team has completed its planned checks. Planned delivery: 2026-12-15. Deadline: 2026-12-20. Ada owns the release and records the review notes.'),
          ('zh','示範專案目前按照時程推進，團隊已完成規劃的檢查。預計交付日為2026-12-15，截止日期為2026-12-20。負責人為小安，會議記錄由助理整理，驗收範圍包含資料查詢與權限管理。')]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--n-probs',type=int,default=256);parser.add_argument('--output',default='/tmp/j-infrastructure-smoke.json');args=parser.parse_args()
    plan=json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text());config=json.loads(Path('data/synthetic-v2/config.json').read_text());model=plan['models']['e2b']
    plan['n_probs']=args.n_probs
    path=hf_hub_download(model['model_id'],model['file'],revision=model['revision'],local_files_only=True)
    output=Path(args.output)
    if output.exists():raise ValueError('Use a new probe output file')
    with output.with_suffix('.server.log').open('w') as log:
        cmd=['/workspace/llama.cpp/build/bin/llama-server','-m',path,'--host','127.0.0.1','--port','8084','-ngl','0','-t','4','-tb','4','-c','4096','-np','1','--swa-full','--no-webui','-b','512','-ub','512']
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);session=requests.Session();session.trust_env=False
        try:
            for _ in range(180):
                if proc.poll() is not None:raise RuntimeError('server exited')
                try:
                    if session.get('http://127.0.0.1:8084/health',timeout=2).status_code==200:break
                except requests.RequestException:pass
                time.sleep(1)
            else:raise RuntimeError('server health timeout')
            arm=JArm(plan,config,'e2b','http://127.0.0.1:8084');results=[]
            for lang,text in FIXTURES:
                for cache in (False,True):
                    result=arm.score_j(text,lang,cache_prompt=cache);results.append(result)
                    print(lang,cache,'latency_ms',result['latency_ms'],'tokens',result['prompt_tokens'],'missing',result['missing'],flush=True)
            deltas=[abs(results[i]['score']-results[i+1]['score']) for i in (0,2) if results[i]['score'] is not None and results[i+1]['score'] is not None]
            output.write_text(json.dumps({'purpose':'Infrastructure smoke; not corpus evaluation or formal 100-row cost benchmark',
                'fixtures':FIXTURES,'model':model,'n_probs':args.n_probs,'results':results,'max_cached_uncached_score_delta':max(deltas) if deltas else None},ensure_ascii=False,indent=2)+'\n')
        finally:
            proc.terminate()
            try:proc.wait(timeout=15)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()

if __name__=='__main__':main()

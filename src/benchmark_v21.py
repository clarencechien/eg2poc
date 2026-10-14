"""Same-machine 100-row latency benchmark; run without concurrent inference."""
import gc
import json
import time
from pathlib import Path
import numpy as np
from .arms import EmbeddingArms,NLIArm,probabilities,cosine_distance
from .common import read_jsonl,write_jsonl,digest


def main():
    import torch
    torch.set_num_threads(4)
    plan=json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text());config=json.loads(Path('data/synthetic-v2/config.json').read_text())
    mapping={p['pair_id']:p for p in read_jsonl('data/synthetic-v2/pairs.jsonl')};rows=[mapping[pid] for pid in plan['benchmark_pair_ids']]
    out=Path('results/synthetic-v2.1');out.mkdir(exist_ok=True)
    if (out/'benchmark-small-models.jsonl').exists():raise ValueError('Benchmark already exists; keep measured timings')
    embedding=EmbeddingArms(config['embedding'],config['labels_alt']);embedding.prepare(rows)
    embedding.encode([rows[0]['new_text']],config['embedding']['document_template'],batch_size=1)
    results=[]
    for i,p in enumerate(rows):
        labels=embedding.labels[p['lang'],'classification'];old,_=probabilities(embedding.cache[p['old_text']],labels,config['embedding']['temperature'])
        t=time.perf_counter();newvector=embedding.encode([p['new_text']],config['embedding']['document_template'],batch_size=1)[0]
        t_projection=time.perf_counter();new,_=probabilities(newvector,labels,config['embedding']['temperature']);score=cosine_distance(old,new)
        end=time.perf_counter();formatted=config['embedding']['document_template'].format(text=p['new_text'])
        results.append({'pair_id':p['pair_id'],'arm':'C_alt_classification','latency_ms':(end-t)*1000,
                        'projection_only_ms':(end-t_projection)*1000,'input_tokens':len(embedding.model.tokenizer(formatted)['input_ids']),
                        'score':score,'old_vector_and_labels_prewarmed':True,'new_vector_cached':False})
        if (i+1)%20==0:print(f'C cost benchmark {i+1}/100',flush=True)
    embedding_params=sum(p.numel() for p in embedding.model.parameters());del embedding;gc.collect()
    nli=NLIArm(config['nli']);nli.label_probabilities([(rows[0]['new_text'],label) for label in config['labels_alt'][rows[0]['lang']]])
    for i,p in enumerate(rows):
        pairs=[(p['new_text'],label) for label in config['labels_alt'][p['lang']]]
        t=time.perf_counter();probs=np.asarray(nli.label_probabilities(pairs));score=float(probs[1:,nli.entailment].max());elapsed=(time.perf_counter()-t)*1000
        tokens=nli.tokenizer([a for a,b in pairs],[b for a,b in pairs],padding=False,truncation=False)['input_ids']
        results.append({'pair_id':p['pair_id'],'arm':'D2_alt_single','latency_ms':elapsed,'input_tokens':sum(map(len,tokens)),
                        'label_pairs':4,'forward_calls':1,'batch_size':4,'score':score})
        if (i+1)%20==0:print(f'D2 cost benchmark {i+1}/100',flush=True)
    write_jsonl(out/'benchmark-small-models.jsonl',results)
    (out/'benchmark-small-models-manifest.json').write_text(json.dumps({'plan_sha256':digest('data/synthetic-v2.1/analysis-plan.json'),
       'embedding_model':config['embedding'],'nli_model':config['nli'],'embedding_parameters':embedding_params,
       'nli_parameters':sum(p.numel() for p in nli.model.parameters()),'n_rows_each':100,'cpu_threads':4,'dtype':'float32',
       'method':'Sequential paragraphs after one untimed warmup. EG2 old vectors/labels prewarmed, new embedding measured; NLI four label pairs in one batch. No concurrent inference.',
       'source_sha256':digest(__file__)},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()

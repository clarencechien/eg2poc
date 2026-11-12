"""v0.3 D2 NLI (S task) and C (P task, EG2 float32 label-distribution distance), using the v2 arm code unchanged.

  HF_HOME=.cache/huggingface .venv/bin/python -m src.run_v3_nli_c            # quality
  HF_HOME=.cache/huggingface .venv/bin/python -m src.run_v3_nli_c --bench    # same-machine cost table, run alone

NLI: premise = rendered state, hypothesis = each option text (fixed A-D). Per-option score = P(entail) - P(contradict);
answer = argmax; probs = softmax over P(entail) logits is not available, so probs are P(entail) renormalised over A-D.
Inputs over the NLI context are recorded as null (no silent truncation). NLI is order-invariant, so the Q6 reversed
order is not re-run. C: the v2 C_same_classification score on each P pair.
"""
import argparse
import hashlib
import json
import time

import numpy as np

from src.arms import EmbeddingArms, NLIArm, cosine_distance, probabilities
from src.v3_common import (OUT, PLAN, append_jsonl, benchmark_ids, done_keys, pairs, rendered, status_rows,
                           verify_frozen)

CONFIG = json.load(open('config.json'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bench', action='store_true')
    args = ap.parse_args()
    verify_frozen()
    import torch
    torch.set_num_threads(4)
    rows = status_rows()
    by_id = {r['id']: r for r in rows}
    nli = NLIArm(CONFIG['nli'])
    opts = PLAN['task_S']['options']

    def nli_one(row):
        t = time.perf_counter()
        hyps = [opts[row['lang']][k] for k in 'ABCD']
        try:
            p = nli.label_probabilities([(rendered(row), h) for h in hyps])
        except ValueError as exc:
            return {'id': row['id'], 'order': 'fixed', 'probs': None, 'answer': None, 'error': str(exc), 'final_error': True,
                    'latency_ms': (time.perf_counter() - t) * 1000}
        p = np.asarray(p)
        margin = p[:, nli.entailment] - p[:, nli.contradiction]
        ent = p[:, nli.entailment]
        return {'id': row['id'], 'order': 'fixed', 'answer': 'ABCD'[int(margin.argmax())],
                'probs': dict(zip('ABCD', (ent / ent.sum()).tolist())), 'margin': dict(zip('ABCD', margin.tolist())),
                'latency_ms': (time.perf_counter() - t) * 1000}

    if args.bench:
        ids = benchmark_ids()
        nli_one(by_id[ids[0]])
        lat = sorted(nli_one(by_id[i])['latency_ms'] for i in ids)
        emb = EmbeddingArms(CONFIG['embedding'], {'zh': [opts['zh'][k] for k in 'ABCD'], 'en': [opts['en'][k] for k in 'ABCD']})
        emb.encode([rendered(by_id[ids[0]])], CONFIG['embedding']['document_template'])
        clat = []
        for i in ids:
            t = time.perf_counter()
            emb.encode([rendered(by_id[i])], CONFIG['embedding']['document_template'])
            clat.append((time.perf_counter() - t) * 1000)
        clat.sort()
        res = {'D2_NLI': {'mean_ms': sum(lat) / 100, 'p50_ms': lat[49], 'p95_ms': lat[94]},
               'C_encode_one_text': {'mean_ms': sum(clat) / 100, 'p50_ms': clat[49], 'p95_ms': clat[94]}}
        (OUT / 'D2_NLI').mkdir(parents=True, exist_ok=True)
        (OUT / 'D2_NLI' / 'benchmark.json').write_text(json.dumps(res, indent=1) + '\n')
        print(json.dumps(res))
        return

    out = OUT / 'D2_NLI'
    path = out / 'predictions.jsonl'
    done = done_keys(path)
    todo = [r for r in rows if (r['id'], 'fixed') not in done]
    print(f'NLI {len(todo)} rows', flush=True)
    for i, row in enumerate(todo, 1):
        append_jsonl(path, nli_one(row))
        if i % 100 == 0:
            print(f'NLI {i}/{len(todo)}', flush=True)

    emb = EmbeddingArms(CONFIG['embedding'], {'zh': [opts['zh'][k] for k in 'ABCD'], 'en': [opts['en'][k] for k in 'ABCD']})
    labels = {lang: emb.encode(emb.label_texts[lang], CONFIG['embedding']['classification_template']) for lang in ('zh', 'en')}
    prs = pairs()
    ids = sorted({p[k] for p in prs for k in ('old', 'new')})
    vec = dict(zip(ids, emb.encode([rendered(by_id[i]) for i in ids], CONFIG['embedding']['document_template'])))
    cout = OUT / 'C'
    cout.mkdir(parents=True, exist_ok=True)
    with open(cout / 'pairs.jsonl', 'w') as f:
        for p in prs:
            lang = by_id[p['old']]['lang']
            po, _ = probabilities(vec[p['old']], labels[lang], CONFIG['embedding']['temperature'])
            pn, _ = probabilities(vec[p['new']], labels[lang], CONFIG['embedding']['temperature'])
            f.write(json.dumps({'pair': p['pair'], 'p_changed': cosine_distance(po, pn)}) + '\n')
    src = {f: hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in ('src/run_v3_nli_c.py', 'src/arms.py', 'src/v3_common.py')}
    for d in (out, cout):
        (d / 'manifest.json').write_text(json.dumps({'nli': CONFIG['nli'], 'embedding': CONFIG['embedding'], 'source_sha256': src,
                                                     'torch': torch.__version__}, indent=1) + '\n')
    print('done', flush=True)


if __name__ == '__main__':
    main()

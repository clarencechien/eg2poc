"""v0.3 DM arms: MediaPipe Decision Maker (GLiNER / EG2 backends) on the frozen S task.

  .mpvenv/bin/python -m src.run_v3_dm --backend gliner            # quality run (resumable)
  .mpvenv/bin/python -m src.run_v3_dm --backend gliner --bench    # same-machine cost table, run alone
"""
import argparse
import hashlib
import json
import time

import mediapipe as mp

from src.run_mp_decision import BACKENDS, sha256
from src.v3_common import (OUT, append_jsonl, benchmark_ids, done_keys, instructions, options, order_runs,
                           rendered, status_rows, verify_frozen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', choices=('gliner', 'eg2'), required=True)
    ap.add_argument('--bench', action='store_true')
    args = ap.parse_args()
    verify_frozen()
    spec = BACKENDS[args.backend]
    model = f".cache/models/{spec['file']}"
    if sha256(model) != spec['sha256']:
        raise SystemExit('model sha256 mismatch')
    out = OUT / f'DM_{args.backend}'
    out.mkdir(parents=True, exist_ok=True)
    dec = mp.tasks.decision
    dm = dec.DecisionMaker.create_from_options(dec.DecisionMakerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=model)))
    qs = {(lang, order): dec.ChoiceQuestion(criteria=options(lang, order), instructions=instructions(lang))
          for lang in ('zh', 'en') for order in ('fixed', 'reversed')}
    for q in qs.values():
        dm.prewarm(q)

    def run(row, order):
        t = time.perf_counter()
        try:
            r = dm.evaluate_choice(rendered(row), qs[(row['lang'], order)])
        except Exception as exc:
            return {'id': row['id'], 'order': order, 'probs': None, 'answer': None, 'error': f'{type(exc).__name__}: {exc}'[:300],
                    'final_error': True, 'latency_ms': (time.perf_counter() - t) * 1000}
        return {'id': row['id'], 'order': order, 'probs': dict(r.probabilities), 'answer': r.selected_key,
                'confidence': r.confidence, 'latency_ms': (time.perf_counter() - t) * 1000}

    rows = status_rows()
    if args.bench:
        by_id = {r['id']: r for r in rows}
        ids = benchmark_ids()
        run(by_id[ids[0]], 'fixed')  # untimed warmup
        bench = [run(by_id[i], 'fixed') for i in ids]
        path = out / 'benchmark.jsonl'
        path.write_text(''.join(json.dumps({k: b[k] for k in ('id', 'latency_ms')}) + '\n' for b in bench))
        lat = sorted(b['latency_ms'] for b in bench)
        print(json.dumps({'mean_ms': sum(lat) / len(lat), 'p50_ms': lat[49], 'p95_ms': lat[94]}))
        return
    path = out / 'predictions.jsonl'
    done = done_keys(path)
    jobs = [(r, o) for r, o in order_runs(rows) if (r['id'], o) not in done]
    print(f'{len(jobs)} jobs to run', flush=True)
    for i, (row, order) in enumerate(jobs, 1):
        append_jsonl(path, run(row, order))
        if i % 100 == 0:
            print(f'{i}/{len(jobs)}', flush=True)
    (out / 'manifest.json').write_text(json.dumps({
        'arm': f'DM_{args.backend}', 'mediapipe': mp.__version__, 'model': spec, 'source_sha256': {
            f: hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in ('src/run_v3_dm.py', 'src/v3_common.py')},
        'note': 'latencies in predictions.jsonl were measured while other jobs shared the CPU; use benchmark.jsonl for cost'}, indent=1) + '\n')
    print('done', flush=True)


if __name__ == '__main__':
    main()

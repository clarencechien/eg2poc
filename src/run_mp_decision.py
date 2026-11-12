"""Exploratory D2-DM arm: MediaPipe Decision Maker (on-device) with the EmbeddingGemma 2 backend.

Uses the same frozen v2.1 J scope, instructions and labels_alt as J and the Gemini Decision 1
trial, so the matched-control AUROC can sit next to C/D2/J/GD1. Needs a Python env with
`mediapipe==1.2.3` (Linux also needs the system `libegl1` package for the shared library).
"""
import argparse
import hashlib
import json
import platform
import statistics
import time
from pathlib import Path

import mediapipe as mp

from src.run_decision1 import CONTRASTS, KEYS, auc, matched, read_jsonl

MODEL_URL = ('https://huggingface.co/litert-community/embeddinggemma-2-text-270m-litert-lm/'
             'resolve/{rev}/embeddinggemma-2-text-270m.litertlm')
MODEL_REVISION = '9be6e8b90982095dc05c2bd162e4b954ee4dbac7'


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True, help='path to embeddinggemma-2-text-270m.litertlm')
    ap.add_argument('--output', default='results/mediapipe-decision-eg2')
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()
    dec = mp.tasks.decision
    plan = json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
    config = json.loads(Path('data/synthetic-v2/config.json').read_text())
    rows = read_jsonl('data/synthetic-v2/pairs.jsonl'); rowmap = {r['pair_id']: r for r in rows}
    docs = read_jsonl('data/synthetic-v2/docsets.jsonl')
    scope = json.loads(Path('data/synthetic-v2.1/scoring-scope.json').read_text())['pair_ids'][:args.limit]
    bench_ids = list(dict.fromkeys(r['pair_id'] for r in read_jsonl('results/synthetic-v2.1/benchmark-small-models.jsonl')))
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)

    single_q = {lang: dec.ChoiceQuestion(criteria=dict(zip(KEYS, config['labels_alt'][lang])),
                                         instructions=plan['single_instructions'][lang]) for lang in ('zh', 'en')}
    # BooleanQuestion has only `condition`; use the J paired "yes" option text as the condition.
    paired_q = {lang: dec.BooleanQuestion(condition=plan['paired_options'][lang]['A']) for lang in ('zh', 'en')}

    t0 = time.perf_counter()
    dm = dec.DecisionMaker.create_from_options(dec.DecisionMakerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=args.model)))
    load_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    for q in single_q.values():
        dm.prewarm(q)
    prewarm_ms = (time.perf_counter() - t0) * 1000

    def single(text, lang):
        t = time.perf_counter(); r = dm.evaluate_choice(text, single_q[lang]); ms = (time.perf_counter() - t) * 1000
        return {'score': 1.0 - r.probabilities['on_track'], 'choice': r.selected_key, 'probabilities': r.probabilities,
                'confidence': r.confidence, 'latency_ms': ms}

    def paired(old, new, lang):
        text = f'OLD / 舊版本:\n{old}\n\nNEW / 新版本:\n{new}'
        t = time.perf_counter(); r = dm.evaluate_boolean(text, paired_q[lang]); ms = (time.perf_counter() - t) * 1000
        return {'score': r.probability_true, 'value': r.value, 'confidence': r.confidence, 'latency_ms': ms}

    # Cost table: same 100 paragraphs as results/synthetic-v2.1 benchmark, sequential, one untimed warmup.
    single(rowmap[bench_ids[0]]['new_text'], rowmap[bench_ids[0]]['lang'])
    bench = []
    for pid in bench_ids:
        p = rowmap[pid]
        r = single(p['new_text'], p['lang'])
        bench.append({'pair_id': pid, 'arm': 'DM_eg2_single', 'latency_ms': r['latency_ms'], 'score': r['score']})
    lat = sorted(b['latency_ms'] for b in bench)

    preds, scores = [], {}
    for i, pid in enumerate(scope):
        p = rowmap[pid]
        s, q = single(p['new_text'], p['lang']), paired(p['old_text'], p['new_text'], p['lang'])
        preds.append({'pair_id': pid, 'single': s, 'paired': q})
        scores[pid] = {'DM_eg2_single': s['score'], 'DM_eg2_paired': q['score'], 'DM_eg2_choice': s['choice']}
        if (i + 1) % 200 == 0:
            print(f'{i + 1}/{len(scope)}', flush=True)
    docscore = {}
    if args.limit is None:
        for d in docs:
            docscore[d['docset_id']] = single('\n\n'.join(rowmap[x]['new_text'] for x in d['pair_ids']), d['lang'])

    # Merge every comparable arm already in the repo.
    merged = {pid: dict(scores[pid]) for pid in scope}
    for r in read_jsonl('results/synthetic-v2/scores.jsonl'):
        if r['pair_id'] in merged:
            merged[r['pair_id']].update({k: r[k] for k in ('C_alt_classification', 'D2_alt_single', 'D2_alt_paired')})
    for size in ('e2b', 'e4b'):
        for r in read_jsonl(f'results/synthetic-v2.1/{size}/scores.jsonl'):
            if r['pair_id'] in merged:
                merged[r['pair_id']].update({f'J_{size}_single': r[f'J_{size}_single'], f'J_{size}_paired': r[f'J_{size}_paired']})
    gd1 = Path('results/gemini-decision-1/scores.jsonl')
    if gd1.exists():
        for r in read_jsonl(gd1):
            if r['pair_id'] in merged:
                merged[r['pair_id']].update({'GD1_single': r['GD1_single'], 'GD1_paired': r['GD1_paired']})
    arms = ('DM_eg2_single', 'C_alt_classification', 'D2_alt_single', 'J_e2b_single', 'J_e4b_single', 'GD1_single',
            'DM_eg2_paired', 'D2_alt_paired', 'J_e2b_paired', 'J_e4b_paired', 'GD1_paired')
    table = {c: {a: matched(rows, merged, c, a) for a in arms} for c in CONTRASTS}

    argmax = {}
    for pid in scope:
        p = rowmap[pid]; k = f"{p['category']}-{p['lang']}"
        n, hit = argmax.get(k, (0, 0))
        argmax[k] = (n + 1, hit + (scores[pid]['DM_eg2_choice'] != 'on_track'))

    docset_auc = None
    if docscore:
        pos = [docscore[d['docset_id']]['score'] for d in docs if d['label'] == 1]
        neg = [docscore[d['docset_id']]['score'] for d in docs if d['label'] == 0]
        docset_auc = auc(pos, neg)

    all_lat = [x['single']['latency_ms'] for x in preds] + [x['paired']['latency_ms'] for x in preds]
    summary = {
        'arm': 'DM_eg2 (MediaPipe Decision Maker, EmbeddingGemma 2 text 270M .litertlm, CPU delegate)',
        'mediapipe_version': mp.__version__,
        'model': {'url': MODEL_URL.format(rev=MODEL_REVISION), 'revision': MODEL_REVISION,
                  'sha256': sha256(args.model), 'bytes': Path(args.model).stat().st_size},
        'source_sha256': sha256(__file__),
        'host': {'cpu': platform.processor() or platform.machine(), 'python': platform.python_version()},
        'run_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'load_ms': load_ms, 'prewarm_ms_both_langs': prewarm_ms,
        'benchmark_100': {'mean_ms': statistics.mean(lat), 'p50_ms': lat[len(lat) // 2], 'p95_ms': lat[int(len(lat) * 0.95) - 1],
                          'method': 'same 100 paragraphs as v2.1 cost table; sequential; one untimed warmup; new text only'},
        'all_eval_latency_ms': {'mean': statistics.mean(all_lat), 'n': len(all_lat)},
        'n_pairs': len(scope), 'n_docsets': len(docscore),
        'auroc': {c: {a: {'auc': v[0], 'n_pos': v[1], 'n_neg': v[2]} for a, v in t.items()} for c, t in table.items()},
        'docset_auroc': docset_auc,
        'argmax_non_on_track': {k: {'n': n, 'non_on_track': h} for k, (n, h) in sorted(argmax.items())},
    }
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    with (out / 'predictions.jsonl').open('w') as f:
        for x in preds:
            f.write(json.dumps(x, ensure_ascii=False) + '\n')
    with (out / 'scores.jsonl').open('w') as f:
        for pid in scope:
            f.write(json.dumps({'pair_id': pid, **scores[pid]}, ensure_ascii=False) + '\n')
    with (out / 'benchmark.jsonl').open('w') as f:
        for b in bench:
            f.write(json.dumps(b) + '\n')
    if docscore:
        with (out / 'docset-scores.jsonl').open('w') as f:
            for k, v in docscore.items():
                f.write(json.dumps({'docset_id': k, 'DM_eg2_single': v['score'], 'choice': v['choice'], 'latency_ms': v['latency_ms']}) + '\n')
    print(json.dumps({k: summary[k] for k in ('load_ms', 'prewarm_ms_both_langs', 'benchmark_100', 'docset_auroc')}, indent=1))
    for c, t in table.items():
        print(c, '  '.join(f"{a}={'—' if v[0] is None else f'{v[0]:.3f}'}" for a, v in t.items()))
    print({k: f"{h}/{n}" for k, (n, h) in sorted(argmax.items())})


if __name__ == '__main__':
    main()

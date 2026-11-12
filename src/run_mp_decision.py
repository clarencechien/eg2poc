"""Exploratory D2-DM arms: MediaPipe Decision Maker (on-device) with a chosen backend.

Backends: EmbeddingGemma 2 text 270M (bi-encoder), Laya s512 (multilingual cross-encoder),
GLiNER2.5-Decide s512 (English cross-encoder). Uses the same frozen v2.1 J scope, instructions
and labels_alt as J and the Gemini Decision 1 trial, so matched-control AUROC sits next to
C/D2/J/GD1. Needs `mediapipe==1.2.3` (Linux also needs the system `libegl1` package);
`scripts/setup-mp-decision.sh` installs it and downloads/verifies the model files.
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

BACKENDS = {
    'eg2': {'file': 'embeddinggemma-2-text-270m.litertlm',
            'url': 'https://huggingface.co/litert-community/embeddinggemma-2-text-270m-litert-lm/resolve/'
                   '9be6e8b90982095dc05c2bd162e4b954ee4dbac7/embeddinggemma-2-text-270m.litertlm',
            'revision': 'HF 9be6e8b90982095dc05c2bd162e4b954ee4dbac7',
            'sha256': '2d079ee2f6f066b1f368e8d7c819f55214eaef1d0513b312321901f30ab286fb',
            'note': 'EmbeddingGemma 2 text 270M bi-encoder, int4'},
    'laya': {'file': 'laya_s512.task',
             'url': 'https://storage.googleapis.com/mediapipe-models/decision_maker/laya/float32/laya_s512/latest/laya_s512.task',
             'revision': 'GCS generation 1791232006884043 (latest at 2026-11-12)',
             'sha256': 'e9f1693861c9a79a541d6f716648142ee844fd2e7119c9ed48d166f4b85a15df',
             'note': 'Laya multilingual (mmBERT-base, convaiinnovations/laya@1c5edc17) cross-encoder, 512-token window'},
    'gliner': {'file': 'gliner_s512.task',
               'url': 'https://storage.googleapis.com/mediapipe-models/decision_maker/gliner/float16/gliner_s512/latest/gliner_s512.task',
               'revision': 'GCS generation 1791242707069212 (latest at 2026-11-12)',
               'sha256': '23a02e1b286fab7573ef2a00acbd8bf80fd2b1284de25eb8fafcd74f8bccd7ec',
               'note': 'GLiNER2.5-Decide (DeBERTa-v3 large) cross-encoder, English-only per model card, 512-token window'},
}


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', choices=sorted(BACKENDS), default='eg2')
    ap.add_argument('--model', required=True, help='path to the backend model file')
    ap.add_argument('--output', default=None, help='default results/mediapipe-decision-<backend>')
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()
    spec, arm = BACKENDS[args.backend], f'DM_{args.backend}'
    model_sha = sha256(args.model)
    if model_sha != spec['sha256']:
        raise SystemExit(f'{args.model}: SHA256 {model_sha} differs from pinned {spec["sha256"]}')
    dec = mp.tasks.decision
    plan = json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
    config = json.loads(Path('data/synthetic-v2/config.json').read_text())
    rows = read_jsonl('data/synthetic-v2/pairs.jsonl'); rowmap = {r['pair_id']: r for r in rows}
    docs = read_jsonl('data/synthetic-v2/docsets.jsonl')
    scope = json.loads(Path('data/synthetic-v2.1/scoring-scope.json').read_text())['pair_ids'][:args.limit]
    bench_ids = list(dict.fromkeys(r['pair_id'] for r in read_jsonl('results/synthetic-v2.1/benchmark-small-models.jsonl')))
    out = Path(args.output or f'results/mediapipe-decision-{args.backend}'); out.mkdir(parents=True, exist_ok=True)

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
        t = time.perf_counter()
        try:
            r = dm.evaluate_choice(text, single_q[lang])
        except Exception as exc:  # e.g. GLiNER rejects inputs over its window instead of truncating
            return {'score': None, 'error': f'{type(exc).__name__}: {exc}'[:300], 'latency_ms': (time.perf_counter() - t) * 1000}
        ms = (time.perf_counter() - t) * 1000
        return {'score': 1.0 - r.probabilities['on_track'], 'choice': r.selected_key, 'probabilities': r.probabilities,
                'confidence': r.confidence, 'latency_ms': ms}

    def paired(old, new, lang):
        text = f'OLD / 舊版本:\n{old}\n\nNEW / 新版本:\n{new}'
        t = time.perf_counter()
        try:
            r = dm.evaluate_boolean(text, paired_q[lang])
        except Exception as exc:
            return {'score': None, 'error': f'{type(exc).__name__}: {exc}'[:300], 'latency_ms': (time.perf_counter() - t) * 1000}
        ms = (time.perf_counter() - t) * 1000
        return {'score': r.probability_true, 'value': r.value, 'confidence': r.confidence, 'latency_ms': ms}

    # Cost table: same 100 paragraphs as results/synthetic-v2.1 benchmark, sequential, one untimed warmup.
    single(rowmap[bench_ids[0]]['new_text'], rowmap[bench_ids[0]]['lang'])
    bench = []
    for pid in bench_ids:
        p = rowmap[pid]
        r = single(p['new_text'], p['lang'])
        bench.append({'pair_id': pid, 'arm': f'{arm}_single', 'latency_ms': r['latency_ms'], 'score': r['score']})
    lat = sorted(b['latency_ms'] for b in bench if b['score'] is not None)

    preds, scores = [], {}
    for i, pid in enumerate(scope):
        p = rowmap[pid]
        s, q = single(p['new_text'], p['lang']), paired(p['old_text'], p['new_text'], p['lang'])
        preds.append({'pair_id': pid, 'single': s, 'paired': q})
        scores[pid] = {f'{arm}_single': s['score'], f'{arm}_paired': q['score'], f'{arm}_choice': s.get('choice')}
        if (i + 1) % 200 == 0:
            print(f'{i + 1}/{len(scope)}', flush=True)
    docscore = {}
    if args.limit is None:
        for d in docs:
            docscore[d['docset_id']] = single('\n\n'.join(rowmap[x]['new_text'] for x in d['pair_ids']), d['lang'])

    # Merge every comparable arm already in the repo, including other DM backends.
    merged = {pid: dict(scores[pid]) for pid in scope}
    for r in read_jsonl('results/synthetic-v2/scores.jsonl'):
        if r['pair_id'] in merged:
            merged[r['pair_id']].update({k: r[k] for k in ('C_alt_classification', 'D2_alt_single', 'D2_alt_paired')})
    for size in ('e2b', 'e4b'):
        for r in read_jsonl(f'results/synthetic-v2.1/{size}/scores.jsonl'):
            if r['pair_id'] in merged:
                merged[r['pair_id']].update({f'J_{size}_single': r[f'J_{size}_single'], f'J_{size}_paired': r[f'J_{size}_paired']})
    extra = [('results/gemini-decision-1/scores.jsonl', ('GD1_single', 'GD1_paired'))]
    extra += [(f'results/mediapipe-decision-{b}/scores.jsonl', (f'DM_{b}_single', f'DM_{b}_paired'))
              for b in BACKENDS if b != args.backend]
    present = []
    for path, keys in extra:
        if Path(path).exists():
            present += list(keys)
            for r in read_jsonl(path):
                if r['pair_id'] in merged:
                    merged[r['pair_id']].update({k: r[k] for k in keys})
    arms = ([f'{arm}_single', 'C_alt_classification', 'D2_alt_single', 'J_e2b_single', 'J_e4b_single']
            + [k for k in present if k.endswith('_single')]
            + [f'{arm}_paired', 'D2_alt_paired', 'J_e2b_paired', 'J_e4b_paired'] + [k for k in present if k.endswith('_paired')])
    table = {c: {a: matched(rows, merged, c, a) for a in arms} for c in CONTRASTS}
    by_lang = {lang: {c: {a: matched([r for r in rows if r['lang'] == lang], merged, c, a)
                          for a in (f'{arm}_single', 'D2_alt_single')} for c in CONTRASTS} for lang in ('zh', 'en')}

    argmax = {}
    for pid in scope:
        p = rowmap[pid]; k = f"{p['category']}-{p['lang']}"
        n, hit, miss = argmax.get(k, (0, 0, 0))
        choice = scores[pid][f'{arm}_choice']
        argmax[k] = (n + 1, hit + (choice not in (None, 'on_track')), miss + (choice is None))

    docset_auc = None
    if docscore:
        pos = [docscore[d['docset_id']]['score'] for d in docs if d['label'] == 1 and docscore[d['docset_id']]['score'] is not None]
        neg = [docscore[d['docset_id']]['score'] for d in docs if d['label'] == 0 and docscore[d['docset_id']]['score'] is not None]
        docset_auc = {'auc': auc(pos, neg), 'n_pos': len(pos), 'n_neg': len(neg)}

    all_lat = [x[m]['latency_ms'] for x in preds for m in ('single', 'paired') if x[m]['score'] is not None]
    errors = [x[m]['error'] for x in preds for m in ('single', 'paired') if 'error' in x[m]]
    errors += [v['error'] for v in docscore.values() if 'error' in v]
    summary = {
        'arm': f'{arm} (MediaPipe Decision Maker, CPU delegate)', 'backend': args.backend,
        'mediapipe_version': mp.__version__,
        'model': {**spec, 'bytes': Path(args.model).stat().st_size, 'sha256_verified': True},
        'source_sha256': sha256(__file__),
        'host': {'cpu': platform.processor() or platform.machine(), 'python': platform.python_version()},
        'run_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'load_ms': load_ms, 'prewarm_ms_both_langs': prewarm_ms,
        'benchmark_100': {'mean_ms': statistics.mean(lat), 'p50_ms': lat[len(lat) // 2], 'p95_ms': lat[int(len(lat) * 0.95) - 1],
                          'n_ok': len(lat), 'method': 'same 100 paragraphs as v2.1 cost table; sequential; one untimed warmup; new text only'}
                         if lat else None,
        'all_eval_latency_ms': {'mean': statistics.mean(all_lat), 'n': len(all_lat)} if all_lat else None,
        'n_pairs': len(scope), 'n_docsets': len(docscore), 'n_errors': len(errors), 'error_samples': sorted(set(errors))[:5],
        'missing_single': sum(scores[p][f'{arm}_single'] is None for p in scope),
        'missing_paired': sum(scores[p][f'{arm}_paired'] is None for p in scope),
        'auroc': {c: {a: {'auc': v[0], 'n_pos': v[1], 'n_neg': v[2]} for a, v in t.items()} for c, t in table.items()},
        'auroc_by_lang': {lang: {c: {a: v[0] for a, v in t.items()} for c, t in tl.items()} for lang, tl in by_lang.items()},
        'docset_auroc': docset_auc,
        'argmax_non_on_track': {k: {'n': n, 'non_on_track': h, 'missing': m} for k, (n, h, m) in sorted(argmax.items())},
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
                f.write(json.dumps({'docset_id': k, f'{arm}_single': v['score'], 'choice': v.get('choice'),
                                    'latency_ms': v['latency_ms'], **({'error': v['error']} if 'error' in v else {})},
                                   ensure_ascii=False) + '\n')
    print(json.dumps({k: summary[k] for k in ('load_ms', 'prewarm_ms_both_langs', 'benchmark_100', 'docset_auroc',
                                              'n_errors', 'error_samples', 'missing_single', 'missing_paired')}, indent=1, ensure_ascii=False))
    for c, t in table.items():
        print(c, '  '.join(f"{a}={'—' if v[0] is None else f'{v[0]:.3f}'}" for a, v in t.items()))
    for lang, tl in by_lang.items():
        print(lang, {c: {a: None if v[0] is None else round(v[0], 3) for a, v in t.items()} for c, t in tl.items()})
    print({k: f'{h}/{n}' + (f' (missing {m})' if m else '') for k, (n, h, m) in sorted(argmax.items())})


if __name__ == '__main__':
    main()

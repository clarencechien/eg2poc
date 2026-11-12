"""Post-hoc ceiling analysis of the single-sided decision arms on the frozen v2.1 J scope.

Why: matched-control AUROC is ~1.0 for GD1 / DM-GLiNER / J on T6-T8, so the main table no
longer separates them. This reports (1) recall at a fixed false-positive budget set on the
confirmed negatives, (2) recall at the naive 0.5 threshold, and (3) how many T6 positives still
contain an explicit on-track sentence (a sign the authored label is contestable).
Reads existing outputs only; no inference, no API calls. Exploratory, not pre-registered.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ARMS = {
    'GD1_single': 'results/gemini-decision-1/scores.jsonl',
    'DM_gliner_single': 'results/mediapipe-decision-gliner/scores.jsonl',
    'DM_eg2_single': 'results/mediapipe-decision-eg2/scores.jsonl',
    'DM_laya_single': 'results/mediapipe-decision-laya/scores.jsonl',
    'J_e4b_single': 'results/synthetic-v2.1/e4b/scores.jsonl',
    'J_e2b_single': 'results/synthetic-v2.1/e2b/scores.jsonl',
    'D2_alt_single': 'results/synthetic-v2/scores.jsonl',
}
NEGATIVE = ('T0', 'T1', 'T2', 'T3', 'T4')
POSITIVE = ('T5', 'T6', 'T7', 'T8')
ON_TRACK = re.compile(r'進度領先|按計畫|如期|ahead of schedule|on track|on schedule', re.I)


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def main(out=Path('results/decision-ceiling')):
    rows = {r['pair_id']: r for r in read_jsonl('data/synthetic-v2/pairs.jsonl')}
    scope = json.loads(Path('data/synthetic-v2.1/scoring-scope.json').read_text())['pair_ids']
    scores = defaultdict(dict)
    for arm, path in ARMS.items():
        if not Path(path).exists():
            continue
        for r in read_jsonl(path):
            if r['pair_id'] in scope and r.get(arm) is not None:
                scores[r['pair_id']][arm] = r[arm]
    arms = [a for a in ARMS if any(a in s for s in scores.values())]

    result = {'n_scope': len(scope), 'negatives': list(NEGATIVE), 'arms': {}}
    for arm in arms:
        neg = sorted(scores[p][arm] for p in scope if rows[p]['category'] in NEGATIVE and arm in scores[p])
        thr0, thr1 = neg[-1], neg[int(len(neg) * 0.99) - 1]
        entry = {'n_neg': len(neg), 'neg_max': thr0, 'neg_p99': thr1, 'neg_fp_at_0.5': sum(v > 0.5 for v in neg), 'recall': {}}
        for cat in POSITIVE:
            vals = [scores[p][arm] for p in scope if rows[p]['category'] == cat and arm in scores[p]]
            entry['recall'][cat] = {'n': len(vals), 'at_0.5': sum(v > 0.5 for v in vals),
                                    'at_zero_fp': sum(v > thr0 for v in vals), 'at_1pct_fp': sum(v > thr1 for v in vals)}
        result['arms'][arm] = entry

    t6 = Counter()
    by_form = defaultdict(Counter)
    for p in scope:
        r = rows[p]
        if r['category'] != 'T6':
            continue
        keeps = bool(ON_TRACK.search(r['new_text']))
        t6[(r['strength'], 'n')] += 1
        t6[(r['strength'], 'keeps_on_track_sentence')] += keeps
        if 'GD1_single' in scores[p]:
            t6[(r['strength'], 'gd1_at_or_below_0.5')] += scores[p]['GD1_single'] <= 0.5
        for arm in ('GD1_single', 'DM_gliner_single'):
            if arm in scores[p]:
                by_form[f"{r['lang']}:{r['subcategory']}"][arm + '_n'] += 1
                by_form[f"{r['lang']}:{r['subcategory']}"][arm] += scores[p][arm] > 0.5
    result['t6_contradiction'] = {f'{s}:{k}': v for (s, k), v in sorted(t6.items())}
    result['t6_by_form_at_0.5'] = {k: dict(v) for k, v in sorted(by_form.items())}

    out.mkdir(parents=True, exist_ok=True)
    (out / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for arm, e in result['arms'].items():
        print(arm, f"FP@0.5={e['neg_fp_at_0.5']}", ' '.join(
            f"{c}:{v['at_0.5']}/{v['at_zero_fp']}/{v['at_1pct_fp']} of {v['n']}" for c, v in e['recall'].items()))
    print(result['t6_contradiction'])


if __name__ == '__main__':
    main()

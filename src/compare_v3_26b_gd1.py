"""Exploratory (not pre-registered): J-26B vs GD1 head-to-head on v0.3, from stored predictions only.

  .mpvenv/bin/python -m src.compare_v3_26b_gd1
Reports the paired gap on test and on all originals (calibration + test; no accuracy tuning used either split),
per hard type, agreement, shared errors, and the error-rate ratio. Writes results/synthetic-v3/26b-vs-gd1.json.
"""
import json
from collections import Counter

from src.report_v3 import diff_ci
from src.v3_common import OUT, read_jsonl, status_rows, verify_frozen


def main():
    verify_frozen()
    rows = [r for r in status_rows() if r['variant'] == 'original']
    p = {a: {x['id']: x['answer'] for x in read_jsonl(OUT / a / 'predictions.jsonl') if x['order'] == 'fixed'} for a in ('J_26b', 'GD1', 'J_e4b')}
    res = {}
    for name, sub in (('test', [r for r in rows if r['split'] == 'test']), ('all_originals', rows)):
        items = [(r['pair_id'] or r['id'], int(p['GD1'][r['id']] == r['gold']), int(p['J_26b'][r['id']] == r['gold'])) for r in sub]
        d = diff_ci(items)
        n = len(sub)
        e_gd1, e_26b = sum(1 - a for _, a, _ in items), sum(1 - b for _, _, b in items)
        res[name] = {'n': n, 'acc_gd1': 1 - e_gd1 / n, 'acc_26b': 1 - e_26b / n, 'errors_gd1': e_gd1, 'errors_26b': e_26b,
                     'gap_gd1_minus_26b': d['gap'], 'ci95': d['ci95'], 'mcnemar_p': d['mcnemar_p'],
                     'gd1_only_right': d['a_only'], '26b_only_right': d['b_only'],
                     'same_answer': sum(p['GD1'][r['id']] == p['J_26b'][r['id']] for r in sub) / n,
                     'both_wrong': sum(p['GD1'][r['id']] != r['gold'] and p['J_26b'][r['id']] != r['gold'] for r in sub),
                     'both_wrong_same_answer': sum(p['GD1'][r['id']] != r['gold'] and p['GD1'][r['id']] == p['J_26b'][r['id']] for r in sub)}
    by = Counter()
    for r in rows:
        for a in ('GD1', 'J_26b'):
            by[(r['hard_type'], a)] += p[a][r['id']] != r['gold']
        by[(r['hard_type'], 'n')] += 1
    res['errors_by_type_all_originals'] = {t: {'n': by[(t, 'n')], 'GD1': by[(t, 'GD1')], 'J_26b': by[(t, 'J_26b')]}
                                           for t in sorted({r['hard_type'] for r in rows})}
    res['both_wrong_items'] = [{'id': r['id'], 'gold': r['gold'], 'GD1': p['GD1'][r['id']], 'J_26b': p['J_26b'][r['id']], 'J_e4b': p['J_e4b'][r['id']]}
                               for r in rows if p['GD1'][r['id']] != r['gold'] and p['J_26b'][r['id']] != r['gold']]
    (OUT / '26b-vs-gd1.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()

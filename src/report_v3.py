"""v0.3 report (protocol-v0.3 §5-§6): metrics and pre-registered decision rules on the frozen data.

  .mpvenv/bin/python -m src.report_v3     (needs numpy + tokenizers for the 512-window flag)
Inputs: results/synthetic-v3/<arm>/predictions.jsonl, pairs-direct.jsonl, C/pairs.jsonl, benchmark files.
"""
import hashlib
import json
import math
import random
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np

from src.power_v3 import mcnemar_exact_p
from src.v3_common import OUT, PLAN, ROOT, pairs, q6_ids, read_jsonl, rendered, status_rows, verify_frozen

ARMS_S = ['J_e2b', 'J_e4b', 'J_26b', 'GD1', 'DM_gliner', 'DM_eg2', 'D2_NLI', 'Rule']
WINDOW_ARMS = {'DM_gliner', 'DM_eg2'}
SEED = PLAN['metrics']['bootstrap']['seed']
REPS = PLAN['metrics']['bootstrap']['reps']


# ---------------------------------------------------------------- loading
def gliner_tokens():
    from tokenizers import Tokenizer
    with zipfile.ZipFile('.cache/models/gliner_s512.task') as z:
        return Tokenizer.from_str(z.read('tokenizer.json').decode())


def over_window(rows):
    tok = gliner_tokens()
    out = {}
    for r in rows:
        extra = PLAN['task_S']['instructions'][r['lang']] + ' '.join(PLAN['task_S']['options'][r['lang']].values())
        out[r['id']] = len(tok.encode(rendered(r)).ids) + len(tok.encode(extra).ids) > 512
    return out


def rule_preds(rows):
    rules = json.loads((ROOT / 'rules.json').read_text())
    pats = [(re.compile(x['pattern'], re.I), x['label']) for x in rules['rules']]
    out = {}
    for r in rows:
        lab = next((l for p, l in pats if p.search(rendered(r))), rules['default'])
        probs = {k: float(k == lab) for k in 'ABCD'}
        for order in ('fixed', 'reversed'):
            out[(r['id'], order)] = {'answer': lab, 'probs': probs}
    return out


def load_arm(arm, rows, window):
    if arm == 'Rule':
        return rule_preds(rows)
    p = OUT / arm / 'predictions.jsonl'
    if not p.exists():
        return None
    out = {}
    for x in read_jsonl(p):
        if x.get('probs') is None:
            out[(x['id'], x['order'])] = {'answer': None, 'probs': None}
            continue
        if arm in WINDOW_ARMS and window.get(x['id']):
            out[(x['id'], x['order'])] = {'answer': None, 'probs': None, 'over_window': True}
            continue
        probs = {k: float(x['probs'].get(k, 0.0)) for k in 'ABCD'}
        s = sum(probs.values()) or 1.0
        probs = {k: v / s for k, v in probs.items()}
        out[(x['id'], x['order'])] = {'answer': max(probs, key=probs.get), 'probs': probs}
    if arm == 'D2_NLI':  # order-invariant by construction: reuse fixed for reversed
        for (i, o), v in list(out.items()):
            out[(i, 'reversed')] = v
    return out


# ---------------------------------------------------------------- statistics
def acc_ci(items, correct):
    """items: list of (unit, ok) with ok in {0,1}; cluster bootstrap by unit."""
    if not items:
        return None
    by = defaultdict(list)
    for u, ok in items:
        by[u].append(ok)
    units = sorted(by)
    rng = random.Random(SEED)
    vals = []
    for _ in range(REPS):
        s = n = 0
        for u in (units[rng.randrange(len(units))] for _ in units):
            s += sum(by[u]); n += len(by[u])
        vals.append(s / n)
    vals.sort()
    return {'acc': sum(ok for _, ok in items) / len(items), 'n': len(items),
            'ci95': [vals[int(REPS * 0.025)], vals[int(REPS * 0.975) - 1]]}


def diff_ci(items):
    """items: list of (unit, ok_a, ok_b); returns gap a-b, cluster-bootstrap CI, exact McNemar."""
    if not items:
        return None
    by = defaultdict(list)
    for u, a, b in items:
        by[u].append(a - b)
    units = sorted(by)
    rng = random.Random(SEED + 7)
    vals = []
    for _ in range(REPS):
        s = n = 0
        for u in (units[rng.randrange(len(units))] for _ in units):
            s += sum(by[u]); n += len(by[u])
        vals.append(s / n)
    vals.sort()
    b = sum(1 for _, x, y in items if x and not y)
    c = sum(1 for _, x, y in items if y and not x)
    gap = (b - c) / len(items)
    return {'gap': gap, 'n': len(items), 'a_only': b, 'b_only': c, 'mcnemar_p': mcnemar_exact_p(b, c),
            'ci95': [vals[int(REPS * 0.025)], vals[int(REPS * 0.975) - 1]]}


def verdict(d, ci_a=None, ci_b=None):
    """protocol §6: clearly = gap >= 0.05 and McNemar p < 0.05; comparable = per-arm CIs overlap and p >= 0.05
    (and |gap| < 0.05); everything else is reported as not distinguishable / underpowered, never as comparable."""
    if d is None:
        return 'n/a'
    if d['gap'] >= 0.05 and d['mcnemar_p'] < 0.05:
        return 'clearly higher'
    if d['gap'] <= -0.05 and d['mcnemar_p'] < 0.05:
        return 'clearly lower'
    overlap = ci_a is not None and ci_b is not None and ci_a[0] <= ci_b[1] and ci_b[0] <= ci_a[1]
    if d['mcnemar_p'] >= 0.05 and overlap and abs(d['gap']) < 0.05:
        return 'comparable'
    return 'not distinguishable (underpowered)'


def auroc(pos, neg):
    if not pos or not neg:
        return None
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    d = pos[:, None] - neg[None, :]
    return float(((d > 1e-12) + 0.5 * (np.abs(d) <= 1e-12)).mean())


def fit_temperature(pairs_):
    """pairs_: list of (probs dict, gold). Grid search T on log-probs to minimise NLL."""
    best = (None, math.inf)
    for t in np.exp(np.linspace(math.log(0.05), math.log(20), 121)):
        nll = 0.0
        for p, g in pairs_:
            lp = np.log(np.clip([p[k] for k in 'ABCD'], 1e-12, 1)) / t
            lp -= lp.max()
            q = np.exp(lp) / np.exp(lp).sum()
            nll -= math.log(max(q['ABCD'.index(g)], 1e-12))
        if nll < best[1]:
            best = (float(t), nll)
    return best[0]


def calibrated(p, t):
    lp = np.log(np.clip([p[k] for k in 'ABCD'], 1e-12, 1)) / t
    lp -= lp.max()
    q = np.exp(lp) / np.exp(lp).sum()
    return dict(zip('ABCD', q.tolist()))


def ece_brier(pairs_, bins=10):
    if not pairs_:
        return None, None
    conf = np.array([max(p.values()) for p, _ in pairs_])
    ok = np.array([max(p, key=p.get) == g for p, g in pairs_], float)
    ece = 0.0
    for lo in np.linspace(0, 1, bins, endpoint=False):
        m = (conf > lo) & (conf <= lo + 1 / bins)
        if m.any():
            ece += m.mean() * abs(conf[m].mean() - ok[m].mean())
    brier = float(np.mean([sum((p[k] - (k == g)) ** 2 for k in 'ABCD') for p, g in pairs_]))
    return float(ece), brier


# ---------------------------------------------------------------- main
def main():
    verify_frozen()
    rows = status_rows()
    by_id = {r['id']: r for r in rows}
    window = over_window(rows)
    flagged = set(json.loads((ROOT / 'review' / 'reviewer-flagged.json').read_text())['src_ids'])
    preds = {a: load_arm(a, rows, window) for a in ARMS_S}
    arms = [a for a in ARMS_S if preds[a] is not None]
    groups = PLAN['groups']
    orig = [r for r in rows if r['variant'] == 'original']
    test = [r for r in orig if r['split'] == 'test']
    cal = [r for r in orig if r['split'] == 'calibration']

    def u(r):
        return r['pair_id'] or r['id']

    def ok(arm, r, order='fixed'):
        p = preds[arm].get((r['id'], order))
        return None if p is None or p['answer'] is None else int(p['answer'] == r['gold'])

    def acc(arm, subset):
        items = [(u(r), ok(arm, r)) for r in subset if ok(arm, r) is not None]
        res = acc_ci(items, None)
        if res:
            res['coverage'] = len(items) / len(subset)
        return res

    def compare(a, b, subset):
        items = [(u(r), ok(a, r), ok(b, r)) for r in subset if ok(a, r) is not None and ok(b, r) is not None]
        d = diff_ci(items)
        if d:
            ca = acc_ci([(i[0], i[1]) for i in items], None)['ci95']
            cb = acc_ci([(i[0], i[2]) for i in items], None)['ci95']
            d.update(ci95_a=ca, ci95_b=cb, verdict=verdict(d, ca, cb))
        return d

    report = {'n_test': len(test), 'n_cal': len(cal), 'arms': arms, 'over_window_items': sum(window[r['id']] for r in orig)}
    # 1. accuracy tables
    subsets = {'overall': test, **{g: [r for r in test if r['hard_type'] in cs] for g, cs in groups.items()}}
    subsets.update({t['code']: [r for r in test if r['hard_type'] == t['code']] for t in PLAN['hard_types']})
    subsets.update({f'lang:{l}': [r for r in test if r['lang'] == l] for l in ('zh', 'en')})
    report['accuracy'] = {s: {a: acc(a, sub) for a in arms} for s, sub in subsets.items()}
    # sensitivity: drop reviewer-flagged items
    keep = [r for r in test if r['id'] not in flagged]
    report['accuracy_unflagged'] = {s: {a: acc(a, [r for r in sub if r['id'] not in flagged]) for a in arms}
                                    for s, sub in {'overall': keep, **{g: [r for r in keep if r['hard_type'] in cs] for g, cs in groups.items()}}.items()}
    # 2. hypotheses
    hyp = {}
    if {'J_26b', 'J_e4b'} <= set(arms):
        hyp['H12'] = {s: compare('J_26b', 'J_e4b', subsets[s]) for s in ('overall', 'G1', 'G2', 'G3')}
    if 'J_e2b' in arms:
        easy = [t['code'] for t in PLAN['hard_types'] if (report['accuracy'][t['code']]['J_e2b'] or {}).get('acc', 0) >= 0.95]
        hyp['H13'] = {'easy_types': easy}
        if easy and {'J_26b', 'J_e4b'} <= set(arms):
            hyp['H13']['H12_recomputed'] = {g: compare('J_26b', 'J_e4b', [r for r in subsets[g] if r['hard_type'] not in easy])
                                            for g in ('G1', 'G2', 'G3')}
    if {'J_26b', 'DM_gliner'} <= set(arms):
        g12 = subsets['G1'] + subsets['G2']
        d = compare('J_26b', 'DM_gliner', g12)
        hyp['H14'] = {**d, 'pass': d['ci95'][1] < 0.05}
    if 'J_26b' in arms:
        dat = [r for r in test if r['hard_type'] == 'H-dat']
        pre = {r['id']: by_id.get(r['id'] + '-pre') for r in dat}
        items = [(u(r), ok('J_26b', pre[r['id']]), ok('J_26b', r)) for r in dat if pre[r['id']] and ok('J_26b', r) is not None
                 and ok('J_26b', pre[r['id']]) is not None]
        d = diff_ci(items)
        hyp['H15'] = {**d, 'pass': d['gap'] >= 0.08} if d else None
        hyp['H15_all_arms'] = {}
        for a in arms:
            items = [(u(r), ok(a, pre[r['id']]), ok(a, r)) for r in dat if pre[r['id']] and ok(a, r) is not None and ok(a, pre[r['id']]) is not None]
            dd = diff_ci(items)
            hyp['H15_all_arms'][a] = None if dd is None else {k: dd[k] for k in ('gap', 'n', 'mcnemar_p')}
    # Q6 consistency
    q6 = q6_ids()
    cons = {}
    for a in arms:
        vals = []
        for oid in sorted(q6):
            if oid not in by_id:
                continue
            for k in ('r1', 'r2'):
                rid = f'{oid}-{k}'
                if rid not in by_id:
                    continue
                ans = [preds[a].get((i, o), {}).get('answer') for i in (oid, rid) for o in ('fixed', 'reversed')]
                if None in ans:
                    continue
                vals.append(len(set(ans)) == 1)
        cons[a] = {'consistency': sum(vals) / len(vals) if vals else None, 'n': len(vals)}
    report['q6_consistency'] = cons
    if {'GD1', 'J_26b'} <= set(arms):
        d = compare('GD1', 'J_26b', test)
        hyp['H16'] = {**d, 'gd1_consistency': cons['GD1']['consistency'],
                      'pass': d['verdict'] == 'clearly higher' and (cons['GD1']['consistency'] or 0) >= 0.9}
    # twins double-correct
    report['twin_both_correct'] = {}
    tw = defaultdict(list)
    for r in test:
        if r['pair_id']:
            tw[r['pair_id']].append(r)
    for a in arms:
        vals = [all(ok(a, r) == 1 for r in m) for m in tw.values() if len(m) == 2 and all(ok(a, r) is not None for r in m)]
        report['twin_both_correct'][a] = {'rate': sum(vals) / len(vals) if vals else None, 'n': len(vals)}
    # calibration
    report['calibration'] = {}
    for a in arms:
        if a == 'Rule':
            continue
        fit = [(preds[a][(r['id'], 'fixed')]['probs'], r['gold']) for r in cal if preds[a].get((r['id'], 'fixed'), {}).get('probs')]
        tst = [(preds[a][(r['id'], 'fixed')]['probs'], r['gold']) for r in test if preds[a].get((r['id'], 'fixed'), {}).get('probs')]
        t = fit_temperature(fit) if fit else None
        raw = ece_brier(tst)
        calib = ece_brier([(calibrated(p, t), g) for p, g in tst]) if t else (None, None)
        conf = [max(p.values()) for p, _ in tst]
        right = [max(p, key=p.get) == g for p, g in tst]
        err = auroc([c for c, r_ in zip(conf, right) if r_], [c for c, r_ in zip(conf, right) if not r_])
        report['calibration'][a] = {'temperature': t, 'ece_raw': raw[0], 'brier_raw': raw[1], 'ece_cal': calib[0],
                                    'brier_cal': calib[1], 'error_detection_auroc': err}
    # 3. P task
    prs = pairs()
    report['P'] = {}

    def derived(a, p):
        po = preds[a].get((p['old'], 'fixed'), {}).get('probs')
        pn = preds[a].get((p['new'], 'fixed'), {}).get('probs')
        if not po or not pn:
            return None
        return 1 - sum(po[k] * pn[k] for k in 'ABCD')

    direct = {}
    for a in ('J_e2b', 'J_e4b', 'J_26b', 'GD1'):
        f = OUT / a / 'pairs-direct.jsonl'
        if f.exists():
            direct[a] = {x['pair']: x.get('p_changed') for x in read_jsonl(f)}
    if (OUT / 'C' / 'pairs.jsonl').exists():
        direct['C'] = {x['pair']: x['p_changed'] for x in read_jsonl(OUT / 'C' / 'pairs.jsonl')}
    scorers = {f'{a}:derived': (lambda p, a=a: derived(a, p)) for a in arms}
    scorers.update({f'{a}:direct': (lambda p, a=a: direct[a].get(p['pair'])) for a in direct})
    for name, fn in scorers.items():
        sc = {p['pair']: fn(p) for p in prs}
        res = {}
        for split in ('calibration', 'test'):
            sp = [p for p in prs if p['split'] == split and sc[p['pair']] is not None]
            res[split] = sp
        tp = res['test']
        a_ = auroc([sc[p['pair']] for p in tp if p['label']], [sc[p['pair']] for p in tp if not p['label']])
        neg_cal = sorted(sc[p['pair']] for p in res['calibration'] if not p['label'])
        out = {'auroc_test': a_, 'n_test': len(tp), 'coverage': len(tp) / max(1, sum(p['split'] == 'test' for p in prs))}
        for target, q in (('fpr0', 1.0), ('fpr1', 0.99)):
            if not neg_cal:
                continue
            thr = neg_cal[-1] if q == 1.0 else neg_cal[min(len(neg_cal) - 1, int(math.ceil(len(neg_cal) * q)) - 1)]
            pos = [sc[p['pair']] for p in tp if p['label']]
            neg = [sc[p['pair']] for p in tp if not p['label']]
            out[target] = {'threshold': thr, 'test_recall': sum(v > thr for v in pos) / len(pos) if pos else None,
                           'test_fpr': sum(v > thr for v in neg) / len(neg) if neg else None}
        cands = sorted({sc[p['pair']] for p in res['calibration']})
        if cands:
            best = max(cands, key=lambda t: sum((sc[p['pair']] > t) == bool(p['label']) for p in res['calibration']))
            out['acc_test_at_cal_threshold'] = sum((sc[p['pair']] > best) == bool(p['label']) for p in tp) / len(tp) if tp else None
        report['P'][name] = out
    hyp['H17'] = {a: {'derived_auroc': report['P'].get(f'{a}:derived', {}).get('auroc_test'),
                      'direct_auroc': report['P'].get(f'{a}:direct', {}).get('auroc_test')} for a in direct if a != 'C'}
    for a, v in hyp['H17'].items():
        if v['derived_auroc'] is not None and v['direct_auroc'] is not None:
            v['pass'] = v['derived_auroc'] >= v['direct_auroc']
    hyp['H18'] = {n: {'fpr1_test_fpr': v.get('fpr1', {}).get('test_fpr'),
                      'pass': (v.get('fpr1', {}).get('test_fpr') or 0) <= 0.02} for n, v in report['P'].items() if 'fpr1' in v}
    report['hypotheses'] = hyp
    # 4. cost
    cost = {}
    for a in ('DM_gliner', 'DM_eg2', 'J_e2b', 'J_e4b', 'J_26b'):
        f = OUT / a / 'benchmark.jsonl'
        if f.exists():
            lat = sorted(x['latency_ms'] for x in read_jsonl(f))
            cost[a] = {'mean_ms': sum(lat) / len(lat), 'p50_ms': lat[len(lat) // 2], 'p95_ms': lat[int(len(lat) * 0.95) - 1], 'n': len(lat)}
    if (OUT / 'D2_NLI' / 'benchmark.json').exists():
        cost.update(json.loads((OUT / 'D2_NLI' / 'benchmark.json').read_text()))
    gd = [x for x in read_jsonl(OUT / 'GD1' / 'predictions.jsonl') if x.get('latency_ms')] if (OUT / 'GD1' / 'predictions.jsonl').exists() else []
    if gd:
        lat = sorted(x['latency_ms'] for x in gd)
        cost['GD1'] = {'p50_ms': lat[len(lat) // 2], 'p95_ms': lat[int(len(lat) * 0.95) - 1], 'n': len(lat), 'note': 'network included, 8 concurrent'}
    report['cost'] = cost
    report['inputs_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*/predictions.jsonl'))}
    (OUT / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=1, default=float) + '\n')
    print(json.dumps({'overall': {a: (v or {}).get('acc') for a, v in report['accuracy']['overall'].items()},
                      'H12': {k: (v or {}).get('verdict') for k, v in hyp.get('H12', {}).items()}}, indent=1))


if __name__ == '__main__':
    main()

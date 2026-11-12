"""Exploratory (not pre-registered): E4B -> 26B cascade computed from the stored v0.3 predictions, no re-inference.

Rule: answer with J-E4B when its max option probability >= tau, otherwise use J-26B's answer.
tau is chosen on the calibration split only: the lowest-escalation tau whose calibration accuracy is >= J-26B alone
on the same split; then applied once to the test split. Latency assumes sequential E4B then 26B on the same L4
(benchmark means from results/synthetic-v3/J_*/benchmark.jsonl).
  python3 -m src.cascade_v3
"""
import json

from src.v3_common import OUT, read_jsonl, status_rows, verify_frozen


def preds(arm):
    return {(x['id'], x['order']): x for x in read_jsonl(OUT / arm / 'predictions.jsonl')}


def mean_latency(arm):
    lat = [x['latency_ms'] for x in read_jsonl(OUT / arm / 'benchmark.jsonl')]
    return sum(lat) / len(lat)


def evaluate(rows, e4b, b26, tau):
    n = esc = right = 0
    for r in rows:
        pe, pb = e4b[(r['id'], 'fixed')], b26[(r['id'], 'fixed')]
        conf = max(pe['probs'].values())
        use_big = conf < tau
        ans = pb['answer'] if use_big else pe['answer']
        n += 1
        esc += use_big
        right += ans == r['gold']
    return {'tau': tau, 'n': n, 'accuracy': right / n, 'escalated': esc / n}


def main():
    verify_frozen()
    rows = [r for r in status_rows() if r['variant'] == 'original']
    cal = [r for r in rows if r['split'] == 'calibration']
    test = [r for r in rows if r['split'] == 'test']
    e4b, b26 = preds('J_e4b'), preds('J_26b')
    lat_e, lat_b = mean_latency('J_e4b'), mean_latency('J_26b')
    grid = sorted({round(1 - 10 ** -k, 6) for k in (1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6)} | {0.5, 0.6, 0.7, 0.8, 0.85, 0.95})
    base_cal = evaluate(cal, e4b, b26, 2.0)['accuracy']  # tau > 1 => always 26B
    sweep = []
    for t in grid:
        c, s = evaluate(cal, e4b, b26, t), evaluate(test, e4b, b26, t)
        sweep.append({'tau': t, 'cal_accuracy': c['accuracy'], 'cal_escalated': c['escalated'],
                      'test_accuracy': s['accuracy'], 'test_escalated': s['escalated'],
                      'test_mean_latency_ms': lat_e + s['escalated'] * lat_b})
    ok = [x for x in sweep if x['cal_accuracy'] >= base_cal]
    chosen = min(ok, key=lambda x: x['cal_escalated']) if ok else None
    res = {
        'note': 'exploratory, computed from stored predictions; tau chosen on calibration only',
        'latency_ms_mean': {'J_e4b': lat_e, 'J_26b': lat_b},
        'calibration': {'n': len(cal), 'e4b_alone': evaluate(cal, e4b, b26, 0.0)['accuracy'], '26b_alone': base_cal},
        'test': {'n': len(test), 'e4b_alone': evaluate(test, e4b, b26, 0.0)['accuracy'], '26b_alone': evaluate(test, e4b, b26, 2.0)['accuracy']},
        'chosen': chosen, 'sweep': sweep,
    }
    (OUT / 'cascade.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: res[k] for k in ('calibration', 'test', 'chosen', 'latency_ms_mean')}, indent=1))
    for x in sweep:
        print(f"tau={x['tau']:<8} cal acc {x['cal_accuracy']:.3f} esc {x['cal_escalated']:.2f} | test acc {x['test_accuracy']:.3f} "
              f"esc {x['test_escalated']:.2f} lat {x['test_mean_latency_ms']:.0f}ms")


if __name__ == '__main__':
    main()

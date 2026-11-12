"""Exploratory trial: Gemini Decision 1 (hosted Decisions API) on the frozen v2.1 J scope.

Mirrors the J arm questions (same instructions, same labels_alt, same paired options,
same OLD/NEW layout) so scores can sit next to J-E2B/E4B. The API key is read from the
environment and never written to disk or logs.
"""
import argparse
import hashlib
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import requests

ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/decisions'
MODEL = 'gemini-decision-1'
KEYS = ('on_track', 'delayed', 'blocked', 'cancelled')
CONTRASTS = ('T5-word', 'T6-word', 'T6-sentence', 'T7-word', 'T7-sentence', 'T8-sentence', 'T8-paragraph')


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def api_key():
    for name in ('GEMINI_API_KEY', 'GOOGLE_API_KEY', 'gemini_key'):
        if os.environ.get(name):
            return os.environ[name]
    raise SystemExit('No Gemini API key in GEMINI_API_KEY / GOOGLE_API_KEY / gemini_key')


def build(mode, lang, plan, config, new_text, old_text=None):
    if mode in ('single', 'docset'):
        question = {'type': 'choice', 'instructions': plan['single_instructions'][lang],
                    'criteria': dict(zip(KEYS, config['labels_alt'][lang]))}
        return new_text, question
    opts = plan['paired_options'][lang]
    question = {'type': 'noul', 'instructions': plan['paired_instructions'][lang],
                'criteria': {'true_description': opts['A'], 'false_description': opts['B']}}
    return f'OLD / 舊版本:\n{old_text}\n\nNEW / 新版本:\n{new_text}', question


class Client:
    def __init__(self, key):
        self.session = requests.Session()
        self.session.headers.update({'x-goog-api-key': key, 'Content-Type': 'application/json'})

    def ask(self, text, question):
        body = {'model': MODEL, 'input': text, 'questions': {'q': question}}
        for attempt in range(8):
            start = time.perf_counter()
            r = self.session.post(ENDPOINT, json=body, timeout=60)
            latency = (time.perf_counter() - start) * 1000
            if r.status_code == 200:
                data = r.json()
                return {'answer': data['answers']['q'], 'usage': data.get('usage'), 'latency_ms': latency, 'attempts': attempt + 1}
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 2 ** attempt))
                continue
            return {'error': {'status': r.status_code, 'body': r.text[:500]}, 'latency_ms': latency, 'attempts': attempt + 1}
        return {'error': {'status': r.status_code, 'body': 'retries exhausted'}, 'attempts': 8}


def score_of(mode, result):
    a = result.get('answer')
    if not a:
        return None
    if mode == 'paired':
        return a['noul']
    return 1.0 - a['probabilities']['on_track']


def auc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if not len(pos) or not len(neg):
        return None
    diff = pos[:, None] - neg[None, :]
    return float(((diff > 1e-12) + 0.5 * (np.abs(diff) <= 1e-12)).mean())


def matched(rows, scores, contrast, arm):
    """Same matched-base control logic as src/report_v2.matched (T9 excluded)."""
    category, strength = contrast.split('-')
    mapping = {r['pair_id']: r for r in rows}
    pos, controls = [], set()
    for p in rows:
        if p['category'] != category or p['strength'] != strength:
            continue
        if scores.get(p['pair_id'], {}).get(arm) is None:
            continue
        cs = [c for c in p['control_ids'] if mapping[c]['category'] != 'T9' and scores.get(c, {}).get(arm) is not None]
        if not cs:
            continue
        pos.append(scores[p['pair_id']][arm]); controls.update(cs)
    neg = [scores[c][arm] for c in sorted(controls)]
    return auc(pos, neg), len(pos), len(neg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='results/gemini-decision-1')
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--limit', type=int, default=None, help='only first N scope pairs (smoke)')
    args = ap.parse_args()
    plan = json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
    config = json.loads(Path('data/synthetic-v2/config.json').read_text())
    rows = read_jsonl('data/synthetic-v2/pairs.jsonl'); rowmap = {r['pair_id']: r for r in rows}
    docs = read_jsonl('data/synthetic-v2/docsets.jsonl')
    scope = json.loads(Path('data/synthetic-v2.1/scoring-scope.json').read_text())['pair_ids'][:args.limit]
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)

    jobs = []
    for pid in scope:
        p = rowmap[pid]
        for mode in ('single', 'paired'):
            jobs.append((f'{pid}|{mode}', mode, p['lang'], *build(mode, p['lang'], plan, config, p['new_text'], p['old_text'])))
    if args.limit is None:
        for d in docs:
            text = '\n\n'.join(rowmap[x]['new_text'] for x in d['pair_ids'])
            jobs.append((f"{d['docset_id']}|docset", 'docset', d['lang'], *build('docset', d['lang'], plan, config, text)))

    cache_path = out / 'predictions.jsonl'
    cache = {r['id']: r for r in read_jsonl(cache_path)} if cache_path.exists() else {}
    cache = {k: v for k, v in cache.items() if 'answer' in v}
    todo = [j for j in jobs if j[0] not in cache]
    print(f'{len(jobs)} requests, {len(todo)} to run', flush=True)
    client, lock = Client(api_key()), threading.Lock()
    done = [0]

    def run(job):
        jid, mode, lang, text, question = job
        result = client.ask(text, question)
        result.update(id=jid, mode=mode, lang=lang,
                      request_sha256=hashlib.sha256(json.dumps([text, question], ensure_ascii=False).encode()).hexdigest())
        with lock:
            cache[jid] = result
            with cache_path.open('a') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
            done[0] += 1
            if done[0] % 100 == 0:
                print(f'{done[0]}/{len(todo)}', flush=True)

    with ThreadPoolExecutor(args.workers) as pool:
        list(pool.map(run, todo))

    # compact the append-only cache to one line per request
    cache_path.write_text(''.join(json.dumps(cache[j[0]], ensure_ascii=False) + '\n' for j in jobs if j[0] in cache))

    scores = {pid: {'GD1_single': score_of('single', cache.get(f'{pid}|single', {})),
                    'GD1_paired': score_of('paired', cache.get(f'{pid}|paired', {}))} for pid in scope}
    j = {}
    for size in ('e2b', 'e4b'):
        for r in read_jsonl(f'results/synthetic-v2.1/{size}/scores.jsonl'):
            j.setdefault(r['pair_id'], {}).update({f'J_{size}_single': r[f'J_{size}_single'], f'J_{size}_paired': r[f'J_{size}_paired']})
    merged = {pid: {**j.get(pid, {}), **scores[pid]} for pid in scope}
    arms = ('GD1_single', 'J_e2b_single', 'J_e4b_single', 'GD1_paired', 'J_e2b_paired', 'J_e4b_paired')
    table = {c: {a: matched(rows, merged, c, a) for a in arms} for c in CONTRASTS}

    docscore = {}
    if args.limit is None:
        for d in docs:
            docscore[d['docset_id']] = score_of('single', cache.get(f"{d['docset_id']}|docset", {}))
        jd = {size: {r['docset_id']: r[f'J_{size}_single'] for r in read_jsonl(f'results/synthetic-v2.1/{size}/docset-scores.jsonl')} for size in ('e2b', 'e4b')}
        def dauc(src):
            pos = [src[d['docset_id']] for d in docs if d['label'] == 1 and src.get(d['docset_id']) is not None]
            neg = [src[d['docset_id']] for d in docs if d['label'] == 0 and src.get(d['docset_id']) is not None]
            return auc(pos, neg)
        docset_auc = {'GD1': dauc(docscore), 'J_e2b': dauc(jd['e2b']), 'J_e4b': dauc(jd['e4b'])}
    else:
        docset_auc = None

    ok = [r for r in cache.values() if 'answer' in r]
    lat = np.array([r['latency_ms'] for r in ok])
    tokens = sum(r['usage']['total_input_tokens'] for r in ok)
    errors = [r for r in cache.values() if 'error' in r]
    summary = {'model': MODEL, 'endpoint': ENDPOINT, 'run_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'n_requests': len(jobs), 'n_ok': len(ok), 'n_errors': len(errors),
               'error_samples': [r['error'] for r in errors[:5]],
               'latency_ms': {'mean': float(lat.mean()), 'p50': float(np.percentile(lat, 50)), 'p95': float(np.percentile(lat, 95))} if len(lat) else None,
               'total_input_tokens': tokens, 'est_usd_at_0.10_per_M': tokens / 1e6 * 0.10,
               'auroc': {c: {a: {'auc': v[0], 'n_pos': v[1], 'n_neg': v[2]} for a, v in t.items()} for c, t in table.items()},
               'docset_auroc': docset_auc,
               'missing_single': sum(scores[p]['GD1_single'] is None for p in scope),
               'missing_paired': sum(scores[p]['GD1_paired'] is None for p in scope)}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    with (out / 'scores.jsonl').open('w') as f:
        for pid in scope:
            f.write(json.dumps({'pair_id': pid, **scores[pid]}) + '\n')
    if docscore:
        with (out / 'docset-scores.jsonl').open('w') as f:
            for k, v in docscore.items():
                f.write(json.dumps({'docset_id': k, 'GD1_single': v}) + '\n')
    print(json.dumps({k: summary[k] for k in ('n_requests', 'n_ok', 'n_errors', 'latency_ms', 'total_input_tokens', 'est_usd_at_0.10_per_M', 'docset_auroc')}, indent=1))
    for c, t in table.items():
        print(c, '  '.join(f"{a}={'—' if v[0] is None else f'{v[0]:.3f}'}({v[1]}/{v[2]})" for a, v in t.items()))


if __name__ == '__main__':
    main()

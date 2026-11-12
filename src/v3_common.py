"""Shared helpers for v0.3 scoring (protocol-v0.3 §4-§5). Reads only the frozen data/synthetic-v3."""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path('data/synthetic-v3')
OUT = Path('results/synthetic-v3')
PLAN = json.loads((ROOT / 'analysis-plan.json').read_text())
KEYS = ('A', 'B', 'C', 'D')


def read_jsonl(p):
    return [json.loads(line) for line in Path(p).read_text(encoding='utf-8').splitlines() if line.strip()]


def append_jsonl(p, row):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


def verify_frozen():
    m = json.loads((ROOT / 'manifest.json').read_text())
    for name, digest in m['sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f'{name} changed after freeze')
    return m


def status_rows():
    return read_jsonl(ROOT / 'status.jsonl')


def pairs():
    return read_jsonl(ROOT / 'pairs.jsonl')


def q6_ids():
    return set(json.loads((ROOT / 'review' / 'q6-sample.json').read_text())['ids'])


def order_runs(rows):
    """(row, order) jobs: every row in fixed order; Q6 originals and rewrites also in reversed order."""
    q6 = q6_ids()
    jobs = [(r, 'fixed') for r in rows]
    jobs += [(r, 'reversed') for r in rows if r['variant'] in ('r1', 'r2') or (r['variant'] == 'original' and r['id'] in q6)]
    return jobs


def rendered(row):
    return PLAN['task_S']['render_state'][row['lang']].format(today=row['today'], state=row['state'])


def instructions(lang):
    return PLAN['task_S']['instructions'][lang]


def options(lang, order='fixed'):
    opts = PLAN['task_S']['options'][lang]
    keys = KEYS if order == 'fixed' else tuple(reversed(KEYS))
    return {k: opts[k] for k in keys}


def benchmark_ids():
    """100 pre-selected test originals for the same-machine cost table (excludes H-lng: 512-token arms reject it)."""
    p = OUT / 'benchmark-ids.json'
    if p.exists():
        return json.loads(p.read_text())['ids']
    pool = sorted(r['id'] for r in status_rows() if r['variant'] == 'original' and r['split'] == 'test' and r['hard_type'] != 'H-lng')
    ids = sorted(random.Random(PLAN['seed']).sample(pool, 100))
    OUT.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'seed': PLAN['seed'], 'rule': 'seeded sample of test originals excluding H-lng', 'ids': ids}, indent=1) + '\n')
    return ids


def done_keys(path, fields=('id', 'order')):
    if not Path(path).exists():
        return set()
    return {tuple(r[f] for f in fields) for r in read_jsonl(path) if 'error' not in r or r.get('final_error')}

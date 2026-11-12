"""v0.3 data pipeline after authoring: Q6 sampling, blind review batches, comparison, adjudication, freeze.

Subcommands (run from repo root; python3 is enough except where noted):
  merge-lng                 merge H-lng.zh.part.jsonl + H-lng.en.part.jsonl into H-lng.jsonl
  sample-q6                 seeded stratified sample of 100 originals for the paraphrase subset -> review/q6-sample.json
  build [--batch 60]        anonymised, shuffled blind-review batches -> review/batches/b??.jsonl + review/key.json
  compare                   review/answers/b??.jsonl vs gold -> review/disagreements.jsonl + summary
  adjudication [--batch 40] disagreements as adjudication batches -> review/adjudication/batches/a??.jsonl
  finalize                  apply adjudication, write frozen status/pairs/MANIFEST (see protocol §3.4-3.5)

Reviewers never see gold, rationale, hard_type, pair_id, or the original id (ids are opaque r0001...).
"""
import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('data/synthetic-v3')
RAW, REVIEW = ROOT / 'raw', ROOT / 'review'
PLAN = json.loads((ROOT / 'analysis-plan.json').read_text())
SEED = PLAN['seed']
TYPES = [t['code'] for t in PLAN['hard_types']]


def read_jsonl(p):
    return [json.loads(line) for line in Path(p).read_text(encoding='utf-8').splitlines() if line.strip()]


def write_jsonl(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def items():
    out = []
    for code in TYPES:
        out += read_jsonl(RAW / f'{code}.jsonl')
    return out


def split_of(unit):
    return 'calibration' if int(hashlib.sha256(f'v0.3-split:{unit}'.encode()).hexdigest(), 16) % 3 == 0 else 'test'


def render(lang, today, state):
    return PLAN['task_S']['render_state'][lang].format(today=today, state=state)


def variants():
    """Every text the reviewer must judge: originals, H-dat precomputed, Q6 rewrites."""
    rows = []
    for it in items():
        rows.append({'src_id': it['id'], 'variant': 'original', 'lang': it['lang'], 'today': it['today'], 'state': it['state'], 'gold': it['gold']})
        if it['hard_type'] == 'H-dat':
            rows.append({'src_id': it['id'], 'variant': 'precomputed', 'lang': it['lang'], 'today': it['today'],
                         'state': it['state_precomputed'], 'gold': it['gold']})
    q6 = REVIEW / 'q6-rewrites.jsonl'
    if q6.exists():
        gold = {it['id']: it for it in items()}
        for r in read_jsonl(q6):
            for k in ('r1', 'r2'):
                o = gold[r['id']]
                rows.append({'src_id': r['id'], 'variant': k, 'lang': o['lang'], 'today': o['today'], 'state': r[k], 'gold': o['gold']})
    return rows


def cmd_merge_lng(_):
    parts = read_jsonl(RAW / 'H-lng.zh.part.jsonl') + read_jsonl(RAW / 'H-lng.en.part.jsonl')
    parts.sort(key=lambda r: r['id'])
    write_jsonl(RAW / 'H-lng.jsonl', parts)
    print(f'H-lng.jsonl: {len(parts)} items')


def cmd_sample_q6(_):
    rng = random.Random(SEED)
    pool = defaultdict(list)
    for it in items():
        if it['hard_type'] != 'H-lng':
            pool[it['hard_type']].append(it['id'])
    codes = sorted(pool)
    quota = {c: 100 // len(codes) for c in codes}
    for c in codes[: 100 - sum(quota.values())]:
        quota[c] += 1
    chosen = []
    for c in codes:
        chosen += rng.sample(sorted(pool[c]), quota[c])
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / 'q6-sample.json').write_text(json.dumps({'seed': SEED, 'quota': quota, 'ids': sorted(chosen)}, indent=2) + '\n')
    print(f'q6 sample: {len(chosen)} ids, quota {quota}')


def cmd_build(a):
    rows = variants()
    rng = random.Random(SEED + 1)
    rng.shuffle(rows)
    key = {}
    batches = defaultdict(list)
    for i, r in enumerate(rows):
        rid = f'r{i + 1:04d}'
        key[rid] = {k: r[k] for k in ('src_id', 'variant', 'gold')}
        batches[i // a.batch].append({'rid': rid, 'lang': r['lang'],
                                      'question': PLAN['task_S']['instructions'][r['lang']],
                                      'options': PLAN['task_S']['options'][r['lang']],
                                      'text': render(r['lang'], r['today'], r['state'])})
    for b, rs in batches.items():
        write_jsonl(REVIEW / 'batches' / f'b{b + 1:02d}.jsonl', rs)
    (REVIEW / 'key.json').write_text(json.dumps(key, ensure_ascii=False, indent=1) + '\n')
    print(f'{len(rows)} texts in {len(batches)} batches; key written (keep away from reviewers)')


def answers(folder, field='rid'):
    out = {}
    for p in sorted(Path(folder).glob('*.jsonl')):
        for r in read_jsonl(p):
            out[r[field]] = r
    return out


def cmd_compare(_):
    key = json.loads((REVIEW / 'key.json').read_text())
    ans = answers(REVIEW / 'answers')
    missing = sorted(set(key) - set(ans))
    dis = []
    agree = Counter()
    for rid, k in key.items():
        if rid not in ans:
            continue
        ok = ans[rid]['answer'] == k['gold']
        agree[(k['variant'], ok)] += 1
        if not ok:
            dis.append({'rid': rid, **k, 'reviewer_answer': ans[rid]['answer'], 'reviewer_reason': ans[rid].get('reason', '')})
    write_jsonl(REVIEW / 'disagreements.jsonl', dis)
    n = sum(agree.values())
    print(f'answered {n}/{len(key)}; missing {len(missing)}; disagreements {len(dis)} ({len(dis) / max(n, 1):.1%})')
    for v in ('original', 'precomputed', 'r1', 'r2'):
        t = agree[(v, True)] + agree[(v, False)]
        if t:
            print(f'  {v}: disagree {agree[(v, False)]}/{t}')
    by_type = Counter(d['src_id'].rsplit('-', 1)[0] for d in dis if d['variant'] == 'original')
    print('  original disagreements by type:', dict(sorted(by_type.items())))


def cmd_adjudication(a):
    dis = read_jsonl(REVIEW / 'disagreements.jsonl')
    texts = {}
    for r in variants():
        texts[(r['src_id'], r['variant'])] = r
    rationale = {it['id']: it['rationale'] for it in items()}
    rows = []
    for i, d in enumerate(dis):
        r = texts[(d['src_id'], d['variant'])]
        rows.append({'aid': f'a{i + 1:04d}', 'lang': r['lang'], 'question': PLAN['task_S']['instructions'][r['lang']],
                     'options': PLAN['task_S']['options'][r['lang']], 'text': render(r['lang'], r['today'], r['state']),
                     'answer_1': d['gold'], 'reason_1': rationale[d['src_id']],
                     'answer_2': d['reviewer_answer'], 'reason_2': d['reviewer_reason']})
    key = {r['aid']: {'rid': d['rid'], 'src_id': d['src_id'], 'variant': d['variant']} for r, d in zip(rows, dis)}
    for b in range(0, len(rows), a.batch):
        write_jsonl(REVIEW / 'adjudication' / 'batches' / f'a{b // a.batch + 1:02d}.jsonl', rows[b:b + a.batch])
    (REVIEW / 'adjudication' / 'key.json').write_text(json.dumps(key, indent=1) + '\n')
    print(f'{len(rows)} adjudication items')


def cmd_finalize(_):
    raw = {it['id']: it for it in items()}
    key = json.loads((REVIEW / 'key.json').read_text())
    dis = read_jsonl(REVIEW / 'disagreements.jsonl')
    adj_key = json.loads((REVIEW / 'adjudication' / 'key.json').read_text()) if dis else {}
    adj = answers(REVIEW / 'adjudication' / 'answers', 'aid') if dis else {}
    if dis and set(adj_key) - set(adj):
        raise SystemExit('adjudication incomplete')
    dropped = defaultdict(list)  # src_id -> variants dropped
    for aid, k in adj_key.items():
        verdict = adj[aid]['verdict']  # 'answer_1' (gold stands) | 'answer_2' | 'neither'
        if verdict != 'answer_1':
            dropped[k['src_id']].append({'variant': k['variant'], 'verdict': verdict, 'note': adj[aid].get('reason', '')})
    removed = {s for s, v in dropped.items() if any(x['variant'] in ('original', 'precomputed') for x in v)}
    q6 = {r['id']: r for r in read_jsonl(REVIEW / 'q6-rewrites.jsonl')} if (REVIEW / 'q6-rewrites.jsonl').exists() else {}
    status = []
    for iid, it in sorted(raw.items()):
        if iid in removed:
            continue
        unit = it['pair_id'] or iid
        base = {k: it[k] for k in ('id', 'hard_type', 'lang', 'skeleton', 'today', 'state', 'gold', 'pair_id')}
        group = next(g for g, cs in PLAN['groups'].items() if it['hard_type'] in cs)
        status.append({**base, 'group': group, 'variant': 'original', 'split': split_of(unit)})
        if it['hard_type'] == 'H-dat':
            status.append({**base, 'id': iid + '-pre', 'state': it['state_precomputed'], 'group': group, 'variant': 'precomputed', 'split': split_of(unit)})
        if iid in q6:
            bad = {x['variant'] for x in dropped.get(iid, [])}
            for k in ('r1', 'r2'):
                if k not in bad:
                    status.append({**base, 'id': f'{iid}-{k}', 'state': q6[iid][k], 'group': group, 'variant': k, 'split': split_of(unit)})
    # twin pairs whose partner was removed lose their pair status
    alive = Counter(r['pair_id'] for r in status if r['variant'] == 'original' and r['pair_id'])
    for r in status:
        if r['pair_id'] and alive[r['pair_id']] != 2:
            r['pair_id'] = None
    by_id = {r['id']: r for r in status}
    pairs = []
    twins = defaultdict(list)
    for r in status:
        if r['variant'] == 'original' and r['pair_id']:
            twins[r['pair_id']].append(r)
    for pid, (a, b) in sorted((p, sorted(v, key=lambda x: x['id'])) for p, v in twins.items()):
        pairs.append({'pair': f'{pid}', 'old': a['id'], 'new': b['id'], 'label': int(a['gold'] != b['gold']),
                      'change': f"{a['gold']}->{b['gold']}", 'hard_type': a['hard_type'], 'lang': a['lang'], 'split': a['split']})
    for iid in sorted(q6):
        for k in ('r1', 'r2'):
            if iid in by_id and f'{iid}-{k}' in by_id:
                o = by_id[iid]
                pairs.append({'pair': f'{iid}-{k}', 'old': iid, 'new': f'{iid}-{k}', 'label': 0, 'change': 'none',
                              'hard_type': o['hard_type'], 'lang': o['lang'], 'split': o['split']})
    write_jsonl(ROOT / 'status.jsonl', status)
    write_jsonl(ROOT / 'pairs.jsonl', pairs)
    n_dis = len(dis)
    n_rev = len(key)
    manifest = {
        'version': 'v0.3', 'frozen_utc': __import__('time').strftime('%Y-%m-%dT%H:%M:%SZ', __import__('time').gmtime()),
        'review': {'texts_reviewed': n_rev, 'disagreements': n_dis, 'disagreement_rate': n_dis / n_rev,
                   'kill_threshold': PLAN['review']['kill_disagreement_rate'],
                   'adjudication_verdicts': dict(Counter(adj[a]['verdict'] for a in adj)) if dis else {},
                   'removed_items': sorted(removed), 'dropped_variants': dropped},
        'counts': {'status_rows': len(status), 'originals': sum(r['variant'] == 'original' for r in status),
                   'by_type': dict(Counter(r['hard_type'] for r in status if r['variant'] == 'original')),
                   'by_split': dict(Counter(r['split'] for r in status if r['variant'] == 'original')),
                   'by_gold': dict(Counter(r['gold'] for r in status if r['variant'] == 'original')),
                   'pairs': len(pairs), 'pair_positives': sum(p['label'] for p in pairs)},
        'sha256': {f: sha256(ROOT / f) for f in ('status.jsonl', 'pairs.jsonl', 'rules.json', 'analysis-plan.json', 'AUTHORING.md')},
        'raw_sha256': {p.name: sha256(p) for p in sorted(RAW.glob('H-*.jsonl')) if '.part.' not in p.name},
    }
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: manifest[k] for k in ('review', 'counts')}, ensure_ascii=False, indent=1))
    if manifest['review']['disagreement_rate'] > PLAN['review']['kill_disagreement_rate']:
        print('KILL: disagreement rate above threshold; fix rules/items before scoring (protocol §3.4)')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('merge-lng')
    sub.add_parser('sample-q6')
    b = sub.add_parser('build'); b.add_argument('--batch', type=int, default=60)
    sub.add_parser('compare')
    j = sub.add_parser('adjudication'); j.add_argument('--batch', type=int, default=40)
    sub.add_parser('finalize')
    a = ap.parse_args()
    {'merge-lng': cmd_merge_lng, 'sample-q6': cmd_sample_q6, 'build': cmd_build, 'compare': cmd_compare,
     'adjudication': cmd_adjudication, 'finalize': cmd_finalize}[a.cmd](a)


if __name__ == '__main__':
    main()

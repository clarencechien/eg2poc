"""Validate v0.3 authored items (data/synthetic-v3/raw/<code>.jsonl) against protocol-v0.3 §3.

Usage: .mpvenv/bin/python -m src.v3_validate H-noi [H-dis ...]   (no args = all present files)
       .mpvenv/bin/python -m src.v3_validate --partial H-lng path/to/part.jsonl   (per-item checks only)
Token counts use the GLiNER tokenizer inside .cache/models/gliner_s512.task (needs `tokenizers`).
Exit code 1 if any file has errors. Does not score items and never shows the rule baseline.
"""
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('data/synthetic-v3')
PLAN = json.loads((ROOT / 'analysis-plan.json').read_text())
SKELETONS = {'weekly', 'adr', 'ticket', 'meeting', 'prd'}
BANNED = [
    '專案已取消', '專案按計畫進行', '專案進度落後', '專案遭遇阻礙', '專案已經取消',
    'the project is on track', 'the project is delayed', 'the project is blocked', 'the project has been cancelled',
    'project status: on track', 'project status: delayed', 'project status: blocked', 'project status: cancelled',
    '狀態：按計畫', '狀態：延後', '狀態：卡關', '狀態：取消', '專案狀態：',
]
GLINER_TASK = Path('.cache/models/gliner_s512.task')
_tok = None


def tokens(text):
    global _tok
    if _tok is None:
        from tokenizers import Tokenizer
        with zipfile.ZipFile(GLINER_TASK) as z:
            _tok = Tokenizer.from_str(z.read('tokenizer.json').decode())
    return len(_tok.encode(text).ids)


def render(item, field='state'):
    return PLAN['task_S']['render_state'][item['lang']].format(today=item['today'], state=item[field])


def validate(code, path=None, partial=False):
    spec = next(t for t in PLAN['hard_types'] if t['code'] == code)
    path = Path(path) if path else ROOT / 'raw' / f'{code}.jsonl'
    errors, warnings = [], []
    if not path.exists():
        return [f'{path} missing'], []
    items = []
    for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append(f'line {i}: invalid JSON ({exc})')
    prefix = f"s-{code.lower()}-"
    options = {lang: [o.lower() for o in PLAN['task_S']['options'][lang].values()] for lang in ('zh', 'en')}
    ids, states = set(), set()
    for it in items:
        iid = it.get('id', '?')
        need = ['id', 'task', 'hard_type', 'lang', 'skeleton', 'today', 'state', 'gold', 'pair_id', 'rationale']
        if code == 'H-dat':
            need.append('state_precomputed')
        for k in need:
            if k not in it:
                errors.append(f'{iid}: missing field {k}')
        if errors and errors[-1].startswith(f'{iid}: missing'):
            continue
        if not re.fullmatch(re.escape(prefix) + r'\d{3}', iid):
            errors.append(f'{iid}: id must look like {prefix}001')
        if iid in ids:
            errors.append(f'{iid}: duplicate id')
        ids.add(iid)
        if it['task'] != 'status' or it['hard_type'] != code:
            errors.append(f'{iid}: task must be "status" and hard_type "{code}"')
        if it['lang'] not in ('zh', 'en'):
            errors.append(f'{iid}: lang must be zh or en')
        if it['skeleton'] not in SKELETONS:
            errors.append(f'{iid}: skeleton must be one of {sorted(SKELETONS)}')
        if not re.fullmatch(r'2026-\d{2}-\d{2}', it['today']):
            errors.append(f'{iid}: today must be YYYY-MM-DD in 2026')
        if it['gold'] not in 'ABCD' or len(it['gold']) != 1:
            errors.append(f'{iid}: gold must be one of A B C D')
        if not str(it['rationale']).strip():
            errors.append(f'{iid}: empty rationale')
        state = it['state']
        if re.match(r'\s*(今天|today)\s*[:：]', state, re.I):
            errors.append(f'{iid}: do not put the Today line in state; it is added at render time')
        low = state.lower()
        for phrase in BANNED:
            if phrase.lower() in low:
                errors.append(f'{iid}: banned conclusion phrase "{phrase}"')
        if it['lang'] in options:
            for o in options[it['lang']]:
                if o in low:
                    errors.append(f'{iid}: state copies an option sentence')
        if state in states:
            errors.append(f'{iid}: duplicate state text')
        states.add(state)
        n_tok = tokens(render(it))
        if code == 'H-lng':
            if n_tok < PLAN['h_lng_min_tokens']['min_tokens_rendered_state']:
                errors.append(f'{iid}: H-lng needs >= 520 GLiNER tokens, has {n_tok}')
        elif n_tok > 480:
            errors.append(f'{iid}: non-long items must stay <= 480 GLiNER tokens, has {n_tok}')
        if code == 'H-dat':
            if it['state_precomputed'] == state:
                errors.append(f'{iid}: state_precomputed must add the computed comparisons')
            if tokens(render(it, 'state_precomputed')) > 480:
                errors.append(f'{iid}: state_precomputed exceeds 480 GLiNER tokens')

    n = len(items)
    if partial:
        return errors, [f'{code} (partial {path}): n={n} gold={dict(sorted(Counter(it.get("gold") for it in items).items()))}']
    if n != spec['n_items']:
        errors.append(f'{code}: has {n} items, needs exactly {spec["n_items"]}')
    langs = Counter(it.get('lang') for it in items)
    if langs['zh'] != langs['en']:
        errors.append(f'{code}: zh/en must be equal, got {dict(langs)}')
    golds = Counter(it.get('gold') for it in items)
    for g in 'ABCD':
        if golds[g] < spec['per_label_min']:
            errors.append(f'{code}: gold {g} has {golds[g]}, needs >= {spec["per_label_min"]}')
    if n and golds['A'] / n > spec['max_share_A']:
        errors.append(f'{code}: gold A share {golds["A"] / n:.2f} > {spec["max_share_A"]}')
    pairs = defaultdict(list)
    for it in items:
        if it.get('pair_id'):
            pairs[it['pair_id']].append(it)
    good_pairs = 0
    for pid, members in pairs.items():
        if not re.fullmatch(re.escape(prefix) + r'p\d{2}', pid):
            errors.append(f'{pid}: pair_id must look like {prefix}p01')
        if len(members) != 2:
            errors.append(f'{pid}: twin pair must have exactly 2 items, has {len(members)}')
            continue
        a, b = members
        if a['gold'] == b['gold']:
            errors.append(f'{pid}: twins must have different gold')
        elif a['lang'] != b['lang']:
            errors.append(f'{pid}: twins must share lang')
        else:
            good_pairs += 1
    if good_pairs < spec['min_twin_pairs']:
        errors.append(f'{code}: {good_pairs} valid twin pairs, needs >= {spec["min_twin_pairs"]}')
    skel = Counter(it.get('skeleton') for it in items)
    if len(skel) < 4:
        errors.append(f'{code}: use at least 4 of the 5 skeletons, got {dict(skel)}')
    summary = f'{code}: n={n} langs={dict(langs)} gold={dict(sorted(golds.items()))} twin_pairs={good_pairs} skeletons={dict(skel)}'
    return errors, [summary] + warnings


def main():
    if sys.argv[1:2] == ['--partial']:
        errors, info = validate(sys.argv[2], sys.argv[3], partial=True)
        print(*info, sep='\n')
        for e in errors:
            print('  ERROR', e)
        print('  OK' if not errors else f'  {len(errors)} errors')
        sys.exit(1 if errors else 0)
    codes = sys.argv[1:] or [t['code'] for t in PLAN['hard_types'] if (ROOT / 'raw' / f"{t['code']}.jsonl").exists()]
    bad = False
    for code in codes:
        errors, info = validate(code)
        for line in info:
            print(line)
        for e in errors:
            print('  ERROR', e)
        print(f'  {code}: {"OK" if not errors else f"{len(errors)} errors"}')
        bad |= bool(errors)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

"""v0.3 GD1 arm: Gemini Decision 1 on the frozen S task (choice) and P direct (noul). Resumable.

  python3 src/run_v3_gd1.py            (needs GEMINI_API_KEY / GOOGLE_API_KEY / gemini_key)
"""
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.run_decision1 import Client, api_key  # noqa: E402
from src.v3_common import (OUT, PLAN, append_jsonl, done_keys, instructions, options, order_runs, pairs,  # noqa: E402
                           read_jsonl, rendered, status_rows, verify_frozen)

V21 = json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
RULES = {lang: PLAN['task_S']['instructions'][lang].split('？', 1)[1] if lang == 'zh'
         else PLAN['task_S']['instructions'][lang].split('? ', 1)[1] for lang in ('zh', 'en')}


def paired_text(old, new):
    return f'OLD / 舊版本:\n{rendered(old)}\n\nNEW / 新版本:\n{rendered(new)}'


def paired_question(lang):
    sep = '' if lang == 'zh' else ' '
    return {'type': 'noul', 'instructions': V21['paired_instructions'][lang] + sep + RULES[lang],
            'criteria': {'true_description': V21['paired_options'][lang]['A'], 'false_description': V21['paired_options'][lang]['B']}}


def main():
    verify_frozen()
    out = OUT / 'GD1'
    out.mkdir(parents=True, exist_ok=True)
    client, lock = Client(api_key()), threading.Lock()
    rows = status_rows()
    by_id = {r['id']: r for r in rows}
    s_path, p_path = out / 'predictions.jsonl', out / 'pairs-direct.jsonl'
    s_done, p_done = done_keys(s_path), done_keys(p_path, ('pair',))
    s_jobs = [(r, o) for r, o in order_runs(rows) if (r['id'], o) not in s_done]
    p_jobs = [p for p in pairs() if (p['pair'],) not in p_done]
    print(f'S jobs {len(s_jobs)}, P jobs {len(p_jobs)}', flush=True)

    def run_s(job):
        row, order = job
        q = {'type': 'choice', 'instructions': instructions(row['lang']), 'criteria': options(row['lang'], order)}
        res = client.ask(rendered(row), q)
        out_row = {'id': row['id'], 'order': order, 'latency_ms': res.get('latency_ms'), 'attempts': res.get('attempts')}
        if 'answer' in res:
            out_row.update(probs=res['answer']['probabilities'], answer=res['answer']['choice'],
                           confidence=res['answer']['confidence'], input_tokens=res['usage']['total_input_tokens'])
        else:
            out_row.update(probs=None, answer=None, error=res['error'], final_error=res['error'].get('status') == 400)
        with lock:
            append_jsonl(s_path, out_row)

    def run_p(p):
        old, new = by_id[p['old']], by_id[p['new']]
        res = client.ask(paired_text(old, new), paired_question(old['lang']))
        out_row = {'pair': p['pair'], 'latency_ms': res.get('latency_ms')}
        if 'answer' in res:
            out_row.update(p_changed=res['answer']['noul'], confidence=res['answer']['confidence'],
                           input_tokens=res['usage']['total_input_tokens'])
        else:
            out_row.update(p_changed=None, error=res['error'], final_error=res['error'].get('status') == 400)
        with lock:
            append_jsonl(p_path, out_row)

    with ThreadPoolExecutor(8) as pool:
        list(pool.map(run_s, s_jobs))
        list(pool.map(run_p, p_jobs))
    s = read_jsonl(s_path)
    p = read_jsonl(p_path)
    tokens = sum(r.get('input_tokens') or 0 for r in s + p)
    print(json.dumps({'S_rows': len(s), 'S_errors': sum('error' in r for r in s), 'P_rows': len(p), 'P_errors': sum('error' in r for r in p),
                      'input_tokens': tokens, 'usd_at_0.10_per_M': tokens / 1e6 * 0.10}), flush=True)


if __name__ == '__main__':
    main()

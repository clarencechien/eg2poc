"""v0.3 J ladder on Modal L4 (protocol-v0.3 §4): Gemma 4 E2B / E4B / 26B-A4B via jevlike decide/ (pinned 9838918).

  JEVLIKE_DIR=/path/to/jevlike@9838918 MODAL_TOKEN_ID=$modal MODAL_TOKEN_SECRET=$modal_secret \
    .modalvenv/bin/modal run src/modal_v3_j.py::ladder [--limit 10]
  .modalvenv/bin/modal volume get eg2poc-v3-results v3 results/synthetic-v3/modal/

Model files come from jevlike's existing volume (gb10-decide-models) and are SHA256-checked against the pinned HF
revisions in data/synthetic-v3/analysis-plan.json before use. One server slot, requests sent sequentially, so
batching cannot change the numerics; the cost table (benchmark) runs afterwards with the prompt cache off.
"""
import hashlib
import json
import os
import subprocess
import time
import urllib.request

import modal

JEVLIKE_DIR = os.environ.get('JEVLIKE_DIR', '')
BUILD_DIR = '/models/llama-b11371'
SERVER_BIN = f'{BUILD_DIR}/bin/llama-server'
FILES = {'e2b': ('gemma-4-E2B-it-Q8_0.gguf', '605d3c2647d7c58c1e4b5375ccb5702acf94c2611b4c8d4877812f8fdd32d053'),
         'e4b': ('gemma-4-E4B-it-Q8_0.gguf', 'f8854aa4480df62585a279e7ca0a881554fc18a41c59c4f62642d16a2ae47012'),
         '26b': ('gemma-4-26B-A4B-it-UD-Q4_K_M.gguf', 'f2c28b3dc4776931ac6f879e11f203dec637ea0f14267a86ec8f6165f63f293f')}
PORT = 8080
N_PROBS = 256

app = modal.App('eg2poc-v3-j')
models = modal.Volume.from_name('gb10-decide-models', create_if_missing=False)
results = modal.Volume.from_name('eg2poc-v3-results', create_if_missing=True)
image = (modal.Image.from_registry('nvidia/cuda:12.8.1-devel-ubuntu22.04', add_python='3.11')
         .entrypoint([]).apt_install('libgomp1').pip_install('numpy', 'requests'))
if JEVLIKE_DIR:
    image = (image.add_local_dir(f'{JEVLIKE_DIR}/decide', remote_path='/root/decide')
             .add_local_file('src/v3_common.py', '/root/src/v3_common.py').add_local_file('src/__init__.py', '/root/src/__init__.py')
             .add_local_dir('data/synthetic-v3', remote_path='/root/data/synthetic-v3')
             .add_local_file('data/synthetic-v2.1/analysis-plan.json', '/root/data/synthetic-v2.1/analysis-plan.json')
             .add_local_file('results/synthetic-v3/benchmark-ids.json', '/root/results/synthetic-v3/benchmark-ids.json'))


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 24), b''):
            h.update(chunk)
    return h.hexdigest()


def _start(path):
    os.environ['LD_LIBRARY_PATH'] = f'{BUILD_DIR}/bin:' + os.environ.get('LD_LIBRARY_PATH', '')
    cmd = [SERVER_BIN, '-m', path, '-ngl', '99', '-c', '8192', '-np', '1', '--port', str(PORT), '--host', '127.0.0.1',
           '--jinja', '--reasoning-budget', '0', '--swa-full']
    log = open('/tmp/server.log', 'w')
    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
    t0 = time.time()
    for _ in range(1500):
        if proc.poll() is not None:
            print(open('/tmp/server.log').read()[-4000:], flush=True)
            raise RuntimeError(f'llama-server exited with {proc.returncode}')
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{PORT}/health', timeout=1)
            return proc, round(time.time() - t0, 1), cmd
        except Exception:  # noqa: BLE001
            time.sleep(1)
    proc.terminate()
    raise RuntimeError('llama-server did not become healthy')


@app.function(image=image, gpu='L4', volumes={'/models': models, '/results': results}, timeout=60 * 60 * 3)
def run(model: str, limit: int = 0, root: str = 'v3'):
    import sys
    sys.path.insert(0, '/root')
    os.chdir('/root')
    import requests
    from decide import client, prompt
    from src.v3_common import (PLAN, benchmark_ids, instructions, options, order_runs, pairs, read_jsonl, rendered,
                               status_rows, verify_frozen)
    verify_frozen()
    fname, want = FILES[model]
    path = f'/models/{fname}'
    t0 = time.time()
    got = _sha256(path)
    if got != want:
        raise RuntimeError(f'{fname}: sha256 {got} != pinned {want}')
    sha_s = round(time.time() - t0, 1)
    v21 = json.load(open('data/synthetic-v2.1/analysis-plan.json'))
    rules = {'zh': PLAN['task_S']['instructions']['zh'].split('？', 1)[1], 'en': PLAN['task_S']['instructions']['en'].split('? ', 1)[1]}
    out = f'/results/{root}/J_{model}'
    os.makedirs(out, exist_ok=True)
    proc, start_s, cmd = _start(path)
    try:
        ver = subprocess.run([SERVER_BIN, '--version'], capture_output=True, text=True, env=os.environ)
        url = f'http://127.0.0.1:{PORT}'
        renderer = prompt.TemplateRenderer(url)
        system = {'zh': prompt.SYSTEM, 'en': prompt.SYSTEM_EN}
        sess = requests.Session()
        sess.trust_env = False

        def ask(state, question, lang, letters, cache=True):
            p = renderer.render(state, question, system=system[lang])
            r = client.read_option_probs(url, p, letters, n_probs=N_PROBS, cache_prompt=cache, session=sess)
            return {'probs': r['probs'] if not r['missing'] else None, 'missing': r['missing'], 'option_mass': r['option_mass'],
                    'first_token': r['first_token'], 'latency_ms': r['latency_ms'], 'prompt_tokens': r['prompt_tokens'],
                    'prompt_sha256': hashlib.sha256(p.encode()).hexdigest()}

        rows = status_rows()
        by_id = {r['id']: r for r in rows}
        jobs = order_runs(rows)
        prs = pairs()
        if limit:
            jobs, prs = jobs[:limit], prs[:limit]
        with open(f'{out}/predictions.jsonl', 'w') as f:
            for i, (row, order) in enumerate(jobs, 1):
                q = {'instructions': instructions(row['lang']), 'options': options(row['lang'], order)}
                r = ask(rendered(row), q, row['lang'], list('ABCD'))
                f.write(json.dumps({'id': row['id'], 'order': order, **r,
                                    'answer': max(r['probs'], key=r['probs'].get) if r['probs'] else None}, ensure_ascii=False) + '\n')
                if i % 200 == 0:
                    print(f'{model} S {i}/{len(jobs)}', flush=True)
        with open(f'{out}/pairs-direct.jsonl', 'w') as f:
            for p in prs:
                old, new = by_id[p['old']], by_id[p['new']]
                lang = old['lang']
                sep = '' if lang == 'zh' else ' '
                q = {'instructions': v21['paired_instructions'][lang] + sep + rules[lang], 'options': v21['paired_options'][lang]}
                state = f'OLD / 舊版本:\n{rendered(old)}\n\nNEW / 新版本:\n{rendered(new)}'
                r = ask(state, q, lang, ['A', 'B'])
                f.write(json.dumps({'pair': p['pair'], **r, 'p_changed': r['probs']['A'] if r['probs'] else None}, ensure_ascii=False) + '\n')
        # cost table: same 100 paragraphs, sequential, prompt cache off, one untimed warmup
        ids = benchmark_ids()
        wq = {'instructions': instructions(by_id[ids[0]]['lang']), 'options': options(by_id[ids[0]]['lang'])}
        ask(rendered(by_id[ids[0]]), wq, by_id[ids[0]]['lang'], list('ABCD'), cache=False)
        with open(f'{out}/benchmark.jsonl', 'w') as f:
            for i in ids:
                row = by_id[i]
                q = {'instructions': instructions(row['lang']), 'options': options(row['lang'])}
                r = ask(rendered(row), q, row['lang'], list('ABCD'), cache=False)
                f.write(json.dumps({'id': i, 'latency_ms': r['latency_ms'], 'prompt_tokens': r['prompt_tokens']}) + '\n')
        smi = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used', '--format=csv,noheader'], capture_output=True, text=True).stdout.strip()
        meta = {'model': model, 'file': fname, 'sha256': got, 'sha256_check_s': sha_s, 'server_cmd': cmd, 'server_start_s': start_s,
                'server_version': (ver.stdout + ver.stderr).strip()[-200:], 'gpu': smi, 'n_probs': N_PROBS,
                'template_server_honored_kwargs': renderer.server_honored_kwargs, 'n_S': len(jobs), 'n_P': len(prs),
                'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        json.dump(meta, open(f'{out}/_run.json', 'w'), indent=1)
        results.commit()
        s = [json.loads(x) for x in open(f'{out}/predictions.jsonl')]
        return {**meta, 'missing_S': sum(r['probs'] is None for r in s),
                'min_option_mass': min(r['option_mass'] for r in s)}
    finally:
        proc.terminate()


@app.local_entrypoint()
def ladder(limit: int = 0, root: str = 'v3'):
    hs = [run.spawn(m, limit, root) for m in ('e2b', 'e4b', '26b')]
    for h in hs:
        print(json.dumps(h.get(), ensure_ascii=False, default=str)[:1500], flush=True)

"""Check complete J outputs against frozen inputs and raw prediction records."""
import argparse
import json
import math
from pathlib import Path

from .common import digest, read_jsonl
from .run_v21 import key
from .run_v2 import verify_data


def require(condition, message):
    if not condition:
        raise ValueError(message)


def indexed(records, field):
    result = {r[field]: r for r in records}
    require(len(result) == len(records), f'Duplicate {field}')
    return result


def validate(root, size):
    root = Path(root) / size
    manifest = json.loads((root / 'manifest.json').read_text())
    require(manifest['status'] == 'complete', f'{size} is incomplete')
    verify_data(Path('data/synthetic-v2'))
    plan_root = Path('data/synthetic-v2.1')
    frozen = json.loads((plan_root / 'manifest.json').read_text())
    for name, expected in frozen['sha256'].items():
        require(digest(plan_root / name) == expected, f'Frozen input changed: {name}')
    require(manifest['plan_sha256'] == digest(plan_root / 'analysis-plan.json'), 'Run used a different plan')
    require(manifest['scope_sha256'] == digest(plan_root / 'scoring-scope.json'), 'Run used a different scope')
    for name, expected in manifest['output_sha256'].items():
        require(digest(root / name) == expected, f'Output hash changed: {name}')
    plan = json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
    scope = json.loads(Path('data/synthetic-v2.1/scoring-scope.json').read_text())
    pairs = indexed(read_jsonl('data/synthetic-v2/pairs.jsonl'), 'pair_id')
    docs = indexed(read_jsonl('data/synthetic-v2/docsets.jsonl'), 'docset_id')
    scores = indexed(read_jsonl(root / 'scores.jsonl'), 'pair_id')
    doc_scores = indexed(read_jsonl(root / 'docset-scores.jsonl'), 'docset_id')
    predictions = indexed(read_jsonl(root / 'predictions.jsonl'), 'key')
    require(set(scores) == set(pairs), 'Scored pair IDs differ from frozen input')
    require(set(doc_scores) == set(docs), 'Scored document IDs differ from frozen input')
    active = set(scope['pair_ids'])
    used = set()
    missing = dict(single=0, paired=0, docset=0)
    for p in predictions.values():
        require(p['model_size'] == size, 'Mixed model predictions')
        letters = 'AB' if p['mode'] == 'paired' else 'ABCD'
        absent = bool(p['missing']) or any(k not in p['probs'] for k in letters)
        require((p['score'] is None) == absent, 'Missing option incorrectly scored')
        if not absent:
            require(all(math.isfinite(p['probs'][k]) and 0 <= p['probs'][k] <= 1 for k in letters), 'Invalid probability')
            require(math.isclose(sum(p['probs'][k] for k in letters), 1, abs_tol=1e-8), 'Probabilities not normalized')
            expected = p['probs']['A'] if p['mode'] == 'paired' else sum(p['probs'][k] for k in 'BCD')
            require(math.isclose(p['score'], expected, abs_tol=1e-12), 'Score differs from probabilities')
    for pid, row in scores.items():
        p = pairs[pid]
        for mode in ('single', 'paired'):
            arm = f'J_{size}_{mode}'
            if pid not in active:
                require(row[arm] is None and 'status' in row, 'Outside-scope row was scored')
                continue
            expected = key(p['lang'], p['new_text'], mode, p['old_text'] if mode == 'paired' else None)
            require(row[f'{mode}_prediction_key'] == expected, 'Prediction attached to wrong input')
            require(row[arm] == predictions[expected]['score'], 'Pair score differs from raw prediction')
            used.add(expected)
            missing[mode] += row[arm] is None
    for did, row in doc_scores.items():
        d = docs[did]
        context = '\n\n'.join(pairs[pid]['new_text'] for pid in d['pair_ids'])
        expected = key(d['lang'], context, 'docset')
        require(row['prediction_key'] == expected, 'Document prediction attached to wrong input')
        require(all(row[k] == d[k] for k in ('label', 'lang', 'matched_set_id')), 'Document ground truth changed')
        require(row[f'J_{size}_single'] == predictions[expected]['score'], 'Document score differs from raw prediction')
        used.add(expected)
        missing['docset'] += row[f'J_{size}_single'] is None
    require(used == set(predictions), 'Unused or missing raw predictions')
    benchmark = read_jsonl(root / 'benchmark.jsonl')
    require([r['pair_id'] for r in benchmark] == plan['benchmark_pair_ids'], 'Benchmark IDs/order differ')
    for row in benchmark:
        require(row['cache_prompt'] is False and row['server_cache_n'] == 0, 'Cost benchmark reused prompt cache')
        require(math.isfinite(row['latency_ms']) and row['latency_ms'] > 0, 'Invalid latency')
        p = pairs[row['pair_id']]
        expected = key(p['lang'], p['new_text'], 'single')
        require(row['score'] == predictions[expected]['score'], 'Benchmark prediction not reused as recorded')
    require(manifest['n_scored_pairs'] == len(active), 'Manifest scoped count differs')
    require(manifest['n_docsets'] == len(docs), 'Manifest document count differs')
    require(manifest['unique_predictions'] == len(predictions), 'Manifest prediction count differs')
    for mode in ('single', 'paired'):
        require(manifest[f'n_missing_{mode}'] == missing[mode], 'Manifest missing count differs')
    return dict(status='passed', model=size, pairs=len(scores), scoped_pairs=len(active),
                docsets=len(docs), predictions=len(predictions), benchmark=len(benchmark), missing=missing)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='results/synthetic-v2.1')
    parser.add_argument('--model-size', choices=['e2b', 'e4b'], required=True)
    args = parser.parse_args()
    result = validate(args.output, args.model_size)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    (Path(args.output) / args.model_size / 'validation.json').write_text(text)
    print(text)


if __name__ == '__main__':
    main()

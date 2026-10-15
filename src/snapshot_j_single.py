"""Publish an immutable completed single stage while paired/T10 continue."""
import argparse
import json
from pathlib import Path

from .common import digest, read_jsonl, write_jsonl
from .report_v2 import CONTRASTS, fmt, matched
from .run_v2 import verify_data
from .run_v21 import key


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-size', choices=['e2b', 'e4b'], required=True)
    args = parser.parse_args()
    size = args.model_size
    verify_data(Path('data/synthetic-v2'))
    plan_root = Path('data/synthetic-v2.1')
    frozen = json.loads((plan_root / 'manifest.json').read_text())
    for name, expected in frozen['sha256'].items():
        if digest(plan_root / name) != expected:
            raise ValueError('Frozen J input changed')
    root = Path('results/synthetic-v2.1') / size
    manifest = json.loads((root / 'manifest.json').read_text())
    if manifest['plan_sha256'] != digest(plan_root / 'analysis-plan.json') or manifest['scope_sha256'] != digest(plan_root / 'scoring-scope.json'):
        raise ValueError('Run plan/scope differs')
    for name, expected in manifest['source_sha256'].items():
        if digest(name) != expected:
            raise ValueError('Scoring source changed')
    scope = set(json.loads((plan_root / 'scoring-scope.json').read_text())['pair_ids'])
    rows = read_jsonl('data/synthetic-v2/pairs.jsonl')
    data = (root / 'predictions.jsonl').read_bytes()
    records = [json.loads(line) for line in data[:data.rfind(b'\n') + 1].splitlines()]
    single = [r for r in records if r['mode'] == 'single']
    predictions = {r['key']: r for r in single}
    expected = {key(r['lang'], r['new_text'], 'single') for r in rows if r['pair_id'] in scope}
    if set(predictions) != expected or len(single) != len(predictions):
        raise ValueError('Single stage incomplete or contains duplicate/unexpected predictions')
    arm = f'J_{size}_single'
    scores = {r['pair_id']: {arm: predictions[key(r['lang'], r['new_text'], 'single')]['score'] if r['pair_id'] in scope else None} for r in rows}
    metrics = {c: matched(rows, scores, c, arm) for c in CONTRASTS}
    languages = {lang: {c: matched(rows, scores, c, arm, lang=lang) for c in CONTRASTS} for lang in ('zh', 'en')}
    missing = sum(p['score'] is None for p in single)
    summary = dict(status='single stage complete; paired/T10 not evaluated by this snapshot', model=size,
                   n_predictions=len(single), n_missing=missing, metrics=metrics, by_language=languages)
    out = root / 'single-stage'
    if out.exists():
        raise ValueError('Snapshot already exists; preserve it unchanged')
    out.mkdir()
    write_jsonl(out / 'predictions.jsonl', single)
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    metadata = dict(manifest)
    metadata.update(status='single_stage_complete', full_run_status_at_snapshot=manifest['status'],
                    n_single=len(single), n_missing_single=missing,
                    output_sha256={name: digest(out / name) for name in ('predictions.jsonl', 'summary.json')})
    (out / 'manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    lines = [f'# {size.upper()} new-only 階段快照', '',
             f'全部 {len(single)} 筆 new-only 已完成，缺值 {missing}。此快照不含 paired 或 T10 結論；完整模型結果以父目錄 manifest 為準。', '',
             '| 配對 | AUROC | 正／負 | 同底稿逐對勝率 |', '|---|---|---|---|']
    for c, m in metrics.items():
        lines.append(f"| {c} | {fmt(m['auc'])} | {m['n_positive']}/{m['n_negative']} | {fmt(m['matched_win_rate'])} |")
    lines += ['', 'AUROC 是配對負例池的排序指標，並非逐對勝率或準確率。資料只有規則合成模板，沒有 Gemini 或獨立覆核；不能外推真實專案。', '',
              '此目錄保存獨立、不可覆寫的原始 single 預測與輸入／程式雜湊；`summary.json` 另含中英分層。完整報告最後會重新由全量結果計算。', '']
    (out / 'report.md').write_text('\n'.join(lines))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

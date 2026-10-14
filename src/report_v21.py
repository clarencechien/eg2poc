"""J results and same-machine costs, with explicit complete-case coverage."""
import json
import argparse
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
from .common import read_jsonl,digest
from .report_v2 import CONTRASTS,matched,fmt
from .run_v2 import verify_data
from .validate_v21 import validate


def describe(values):
    return {'n':len(values),'mean':float(np.mean(values)) if values else None,
            'p50':float(np.median(values)) if values else None,'p95':float(np.percentile(values,95)) if values else None}


def benchmark_cost(root, manifest, plan):
    path=root/'benchmark.jsonl'
    if not path.exists():return None
    data=path.read_bytes()
    records=[json.loads(line) for line in data[:data.rfind(b'\n')+1].splitlines()]
    if len(records)<100:return None
    if [r['pair_id'] for r in records]!=plan['benchmark_pair_ids']:raise ValueError('J benchmark row order differs')
    return {'latency_ms':describe([r['latency_ms'] for r in records]),
            'prefill_ms':describe([r['server_prompt_ms'] for r in records if r['server_prompt_ms'] is not None]),
            'input_tokens':describe([r['prompt_tokens'] for r in records if r['prompt_tokens'] is not None]),
            'model_bytes':manifest['model_bytes'],'quantization':'Q8_0'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='results/synthetic-v2.1');args=parser.parse_args()
    out=Path(args.output);rows=read_jsonl('data/synthetic-v2/pairs.jsonl')
    verify_data(Path('data/synthetic-v2'))
    plan_root=Path('data/synthetic-v2.1')
    frozen=json.loads((plan_root/'manifest.json').read_text())
    for name,expected in frozen['sha256'].items():
        if digest(plan_root/name)!=expected:raise ValueError(f'J frozen input changed: {name}')
    baseline={r['pair_id']:r for r in read_jsonl('results/synthetic-v2/scores.jsonl')}
    base_metrics=json.loads(Path('results/synthetic-v2/metrics.json').read_text())
    plan=json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
    if plan['data_manifest_sha256']!=digest('data/synthetic-v2/manifest.json'):raise ValueError('J data manifest changed')
    summaries={};costs={};hypotheses={};combined={pid:dict(r) for pid,r in baseline.items()}
    for size in ('e2b','e4b'):
        root=out/size
        if not (root/'manifest.json').exists():
            summaries[size]={'status':'not run','reason':'No completed local run'};continue
        manifest=json.loads((root/'manifest.json').read_text())
        if manifest['plan_sha256']!=digest(plan_root/'analysis-plan.json') or manifest['scope_sha256']!=digest(plan_root/'scoring-scope.json'):
            raise ValueError('J scoring plan differs from recorded run')
        cost=benchmark_cost(root,manifest,plan)
        if cost is not None:costs[f'J_{size}']=cost
        if manifest['status']!='complete':
            summaries[size]={'status':manifest['status'],'reason':manifest.get('error','完整品質評估尚未完成；已完成的 100 筆成本測試另列。')};continue
        for name,expected in manifest['output_sha256'].items():
            if digest(root/name)!=expected:raise ValueError(f'J scored output changed: {size}/{name}')
        validate(out,size)
        scores={r['pair_id']:r for r in read_jsonl(root/'scores.jsonl')}
        for pid,r in scores.items():combined[pid].update({k:v for k,v in r.items() if k.startswith('J_')})
        arms=[f'J_{size}_single',f'J_{size}_paired']
        metrics={c:{a:matched(rows,scores,c,a) for a in arms} for c in CONTRASTS}
        langs={lang:{c:{a:matched(rows,scores,c,a,lang=lang) for a in arms} for c in CONTRASTS} for lang in ('zh','en')}
        common={pid:dict(r) for pid,r in baseline.items()}
        jarm=f'J_{size}_single'
        for pid,r in common.items():
            r[jarm]=scores[pid][jarm]
            if r[jarm] is None:r['D2_alt_single']=None
        compare={c:{a:matched(rows,common,c,a) for a in (jarm,'D2_alt_single')} for c in CONTRASTS}
        for c in CONTRASTS:
            j,d=compare[c][jarm]['auc'],compare[c]['D2_alt_single']['auc']
            compare[c]['J_minus_D2']=None if j is None or d is None else j-d
        docrows=read_jsonl(root/'docset-scores.jsonl');valid=[d for d in docrows if d[jarm] is not None]
        docauc=float(roc_auc_score([d['label'] for d in valid],[d[jarm] for d in valid])) if len({d['label'] for d in valid})==2 else None
        selected=('T6-word','T7-word','T8-sentence','T8-paragraph')
        def complete(c):
            m=metrics[c][jarm];expected=base_metrics['primary'][c]['D2_alt_single']
            return m['n_positive']==expected['n_positive'] and m['n_negative']==expected['n_negative']
        h8_numeric=all(metrics[c][jarm]['auc'] is not None and metrics[c][jarm]['auc']>=.85 for c in selected)
        hypotheses[size]={'H8_numeric':h8_numeric,'H8_complete':all(complete(c) for c in selected),
                          'H9_numeric':metrics['T5-word'][jarm]['auc'] is not None and metrics['T5-word'][jarm]['auc']>=.85,'H9_complete':complete('T5-word'),
                          'H10_tie_on_common_cases':all(compare[c]['J_minus_D2'] is not None and abs(compare[c]['J_minus_D2'])<.05 for c in selected),
                          'H10_J_stronger_all':all(compare[c]['J_minus_D2'] is not None and compare[c]['J_minus_D2']>=.05 for c in selected),
                          'H11_numeric_exploratory':docauc is not None and docauc>=.80,'H11_complete':len(valid)==len(docrows)}
        predictions=read_jsonl(root/'predictions.jsonl')
        summaries[size]={'status':'complete','model':manifest['model'],'model_bytes':manifest['model_bytes'],'metrics':metrics,'by_language':langs,'common_case_vs_D2_alt':compare,
                         'T8_with_ambiguous_T9_assumed_negative':{a:matched(rows,scores,'T8-sentence',a,include_t9=True) for a in arms},
                         'docset_auc':docauc,'docset_n_positive':sum(d['label']==1 for d in valid),'docset_n_negative':sum(d['label']==0 for d in valid),
                         'missing_single':manifest['n_missing_single'],'missing_paired':manifest['n_missing_paired'],'n_scored_pairs':manifest['n_scored_pairs'],'n_outside_scope':manifest['n_outside_scope'],
                         'option_mass':describe([r['option_mass'] for r in predictions]),'last_session_seconds':manifest['last_session_seconds']}
    smallpath=out/'benchmark-small-models.jsonl'
    if smallpath.exists():
        records=read_jsonl(smallpath);smallmanifest=json.loads((out/'benchmark-small-models-manifest.json').read_text())
        if smallmanifest['plan_sha256']!=digest(plan_root/'analysis-plan.json'):raise ValueError('Small-model timing plan differs')
        for a,pk in (('C_alt_classification','embedding_parameters'),('D2_alt_single','nli_parameters')):
            values=[r for r in records if r['arm']==a]
            if [r['pair_id'] for r in values]!=plan['benchmark_pair_ids']:raise ValueError('Small-model cost benchmark differs')
            costs[a]={'latency_ms':describe([r['latency_ms'] for r in values]),'input_tokens':describe([r['input_tokens'] for r in values]),'parameters':smallmanifest[pk],'dtype':'float32'}
            if a.startswith('C_'):costs[a]['projection_only_ms']=describe([r['projection_only_ms'] for r in values])
    report={'models':summaries,'hypotheses':hypotheses,'costs':costs,'plan_sha256':digest('data/synthetic-v2.1/analysis-plan.json')}
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# v0.2.1：jevlike J arm 合成試驗','', '依 `main@fb62b10` 的規格追加 J。資料、標籤與配對關係沿用已凍結的 synthetic-v2；沒有新增 Gemini 呼叫。','',
           '目前模型狀態：'+ '；'.join(f"{size.upper()}={info['status']}" for size,info in summaries.items())+'。未完成的品質指標不填零。','',
           'J 使用 `jevlike@9838918533cf3d88dc975ef19d38122b07df47f7` 的既有四選一／布林題介面，未改 prompt 模板。llama.cpp 固定 b11371（99b95488），CPU、4 threads、Q8_0。','',
           '## 主表：專屬負例配對 AUROC','', '| 配對 | C-alt class | D2-alt paired | D2-alt single | J-E2B single | J-E4B single | R |','|---|---|---|---|---|---|---|']
    for c in CONTRASTS:
        values=[base_metrics['primary'][c][a]['auc'] for a in ('C_alt_classification','D2_alt_paired','D2_alt_single')]
        values += [summaries[s].get('metrics',{}).get(c,{}).get(f'J_{s}_single',{}).get('auc') for s in ('e2b','e4b')]
        values.append(base_metrics['primary'][c]['R']['auc'])
        lines.append('| '+c+' | '+' | '.join(fmt(v) for v in values)+' |')
    lines+=['','J 缺少候選選項時保留 null。不同 arm 若有效樣本不同，主表不能直接比較；下方提供每格正／負樣本數及 J／D2 共同有效樣本上的差。所有結論限於合成骨架內。']
    for size,info in summaries.items():
        lines+=['',f'## {size.upper()}','',f"狀態：{info['status']}。"]
        if info['status']!='complete':lines.append(info['reason']);continue
        lines += [f"單邊缺值 {info['missing_single']}/{info['n_scored_pairs']}；配對缺值 {info['missing_paired']}/{info['n_scored_pairs']}。另有 {info['n_outside_scope']} 筆不屬 J 配對評估範圍（T0/T1/T2、T10 個別段落），未跑且保留 null；T10 改評全部 80 組 concat。權重 {info['model_bytes']/1e9:.2f} GB，revision `{info['model']['revision']}`。",'',
                  '| 配對 | single AUROC (正/負) | paired AUROC (正/負) | 共同樣本 J−D2-alt single |','|---|---|---|---|']
        for c in CONTRASTS:
            ms,mp=[info['metrics'][c][f'J_{size}_{k}'] for k in ('single','paired')]
            lines.append(f"| {c} | {fmt(ms['auc'])} ({ms['n_positive']}/{ms['n_negative']}) | {fmt(mp['auc'])} ({mp['n_positive']}/{mp['n_negative']}) | {fmt(info['common_case_vs_D2_alt'][c]['J_minus_D2'])} |")
        lines+=['',f"T10 三段 new concat：AUROC {fmt(info['docset_auc'])}，有效正／負 {info['docset_n_positive']}/{info['docset_n_negative']}。此為合成政策任務，未經獨立判讀。",'',
                '### H8–H11','', '數值門檻與完整覆蓋分開記錄；只在兩者均通過時才可說這批資料滿足該假說。H8 的正式門檻以 E2B 為主，E4B 是後續能力比較。','', '```json',json.dumps(hypotheses[size],ensure_ascii=False,indent=2),'```', '',
                'H10 不平手可能是 J 較強、較弱或各類互有優劣；不能把「不平手」直接解讀為 J 較強，也不能從本資料決定正式架構。']
        for lang in ('zh','en'):
            lines+=['',f'### {lang} single AUROC','', '| 配對 | AUROC | 正/負 |','|---|---|---|']
            for c in CONTRASTS:
                m=info['by_language'][lang][c][f'J_{size}_single'];lines.append(f"| {c} | {fmt(m['auc'])} | {m['n_positive']}/{m['n_negative']} |")
    lines+=['','## 成本：同一台 CPU、同一批 100 筆','', '| arm | 平均端到端 ms | p95 ms | 平均 prefill ms | 平均輸入 tokens | 模型 | prewarm 後可否固定預算 |','|---|---|---|---|---|---|---|']
    for a in ('C_alt_classification','D2_alt_single','J_e2b','J_e4b'):
        if a not in costs:lines.append(f'| {a} | 未跑 | — | — | — | — | — |');continue
        m=costs[a];model=f"{m['parameters']/1e6:.1f}M / float32" if 'parameters' in m else f"{m['model_bytes']/1e9:.2f} GB / Q8_0"
        note='標籤／old 已預算；new embedding 仍隨長度變動' if a.startswith('C_') else ('4 組 premise/hypothesis，單批 forward；仍隨長度變動' if a.startswith('D2_') else '每題一次 prefill；隨輸入長度變動')
        lines.append(f"| {a} | {fmt(m['latency_ms']['mean'])} | {fmt(m['latency_ms']['p95'])} | {fmt(m.get('prefill_ms',{}).get('mean'))} | {fmt(m['input_tokens']['mean'])} | {model} | {note} |")
    lines+=['','所有 arm 先做一次不計時 warmup，再逐段測量；J 的 100 筆成本測試關閉 prompt cache。這 100 筆預測沿用於品質評估，其餘品質推論啟用既有 prefix cache；兩者逐題標記，不能把品質推論的延遲混入成本表。D2 四個標籤以一批計算，token 數是四組總和；J 題目包含標籤與模板，token 數自然不同。EG2 的 old 向量與 label 已預算，時間包含 new embedding；僅有既有向量的投影運算可視為固定維度成本。','',
            '## 限制與可追溯性','', '- J 單邊分類衡量目前是否為風險狀態，不等於一般狀態漂移。資料沒有完整涵蓋「原本已卡關但本次未變」或解除風險的反例。',
            '- 日期跨期正例只改日期，原文「進度領先」仍保留，形成文字敘述與日期值之間的衝突；模型對此的表現不能單獨代表一般日期推理能力。',
            '- T10 使用三個信號同時成立才待審的人工政策，沒有兩個獨立 prompt 判讀，政策也沒送入模型；H11 只能探索。',
            '- `summary.json` 保存中英分層、共同有效樣本比較、候選 option mass 與成本分布；各模型 `predictions.jsonl` 保存每題延遲、token、原始字母 logprob、缺選項及 prompt hash。',
            '- `data/synthetic-v2.1/analysis-plan.json` 保存評分前凍結的題目、標籤順序、模型 revision、100 筆 benchmark IDs。模型 SHA256、引擎 SHA256 與程式 SHA256 見各模型 manifest。','']
    (out/'report.md').write_text('\n'.join(lines))
    cost_start=lines.index('## 成本：同一台 CPU、同一批 100 筆')
    cost_end=lines.index('## 限制與可追溯性')
    summary=lines[:lines.index('J 缺少候選選項時保留 null。不同 arm 若有效樣本不同，主表不能直接比較；下方提供每格正／負樣本數及 J／D2 共同有效樣本上的差。所有結論限於合成骨架內。')]
    summary+=['J 缺選項記 null；有效樣本數、共同樣本比較與 H8–H11 見完整報告。T10 是未獨立覆核的合成政策任務，不能外推真實文件。','']
    summary+=lines[cost_start:cost_end]+['[完整結果、H8–H11、限制](report.md)','']
    (out/'summary.md').write_text('\n'.join(summary))
    print(json.dumps({'hypotheses':hypotheses,'costs':costs},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

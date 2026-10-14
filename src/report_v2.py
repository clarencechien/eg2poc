"""Matched-base evaluation; no model/label selection or threshold tuning."""
import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
from .common import read_jsonl, write_jsonl, digest
from .run_v2 import SETS, PREFIXES, verify_data

CONTRASTS=('T5-word','T6-word','T6-sentence','T7-word','T7-sentence','T8-sentence','T8-paragraph')
C_ARMS=[f'C_{s}_{p}' for s in SETS for p in PREFIXES]
D_ARMS=[f'D2_{s}_{kind}' for s in SETS for kind in ('paired','single')]
ARMS=['A','B768','D1']+C_ARMS+D_ARMS+['R']
COMBOS=[f'final_{s}' for s in SETS]


def matched(rows, scores, contrast, arm, lang=None, skeleton=None, include_t9=False):
    category,strength=contrast.split('-')
    mapping={r['pair_id']:r for r in rows}
    positives=[p for p in rows if p['category']==category and p['strength']==strength and
               (lang is None or p['lang']==lang) and (skeleton is None or p['skeleton']==skeleton)]
    eligible=[];control_ids=set();wins=[]
    for p in positives:
        controls=[cid for cid in p['control_ids'] if include_t9 or mapping[cid]['category']!='T9']
        if scores.get(p['pair_id'],{}).get(arm) is None:continue
        controls=[cid for cid in controls if scores.get(cid,{}).get(arm) is not None]
        if not controls:continue
        eligible.append(p);control_ids.update(controls)
        value=scores[p['pair_id']][arm]
        wins.extend(.5 if abs(value-scores[cid][arm])<1e-12 else float(value>scores[cid][arm]) for cid in controls)
    values=[scores[p['pair_id']][arm] for p in eligible]+[scores[cid][arm] for cid in sorted(control_ids)]
    labels=[1]*len(eligible)+[0]*len(control_ids)
    return {'auc':float(roc_auc_score(labels,values)) if eligible and control_ids else None,
            'n_positive':len(eligible),'n_negative':len(control_ids),'n_requested_positive':len(positives),
            'matched_win_rate':float(np.mean(wins)) if wins else None,'n_matched_comparisons':len(wins)}


def fmt(v):return '—' if v is None else f'{v:.3f}'


def table(metrics, arms, contrasts=CONTRASTS):
    lines=['| 配對 | '+' | '.join(arms)+' |','|---|'+'---|'*len(arms)]
    for c in contrasts:lines.append('| '+c+' | '+' | '.join(fmt(metrics[c][a]['auc']) for a in arms)+' |')
    return lines


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',default='data/synthetic-v2');ap.add_argument('--output',default='results/synthetic-v2');args=ap.parse_args()
    data,out=Path(args.data),Path(args.output);input_manifest=verify_data(data)
    run=json.loads((out/'manifest.json').read_text())
    if run['status']!='complete':raise ValueError('Inference incomplete')
    rows=read_jsonl(data/'pairs.jsonl');results=read_jsonl(out/'scores.jsonl');scores={r['pair_id']:r for r in results}
    assert len(scores)==len(rows)==len(results)
    for r in results:
        assert all(v is None or np.isfinite(v) for k,v in r.items() if k!='pair_id')
    arms=ARMS+COMBOS
    primary={c:{a:matched(rows,scores,c,a) for a in arms} for c in CONTRASTS}
    languages={lang:{c:{a:matched(rows,scores,c,a,lang=lang) for a in arms} for c in CONTRASTS} for lang in ('zh','en')}
    skeletons={sk:{c:{a:matched(rows,scores,c,a,skeleton=sk) for a in arms} for c in CONTRASTS} for sk in ('weekly','adr','ticket','meeting','prd')}
    t9={a:matched(rows,scores,'T8-sentence',a,include_t9=True) for a in ARMS}
    pooled={}
    for c in CONTRASTS:
        category,strength=c.split('-');selected=[p for p in rows if (p['category']==category and p['strength']==strength) or p['category'] in ('T1','T2','T3','T4')]
        pooled[c]={}
        for a in ARMS:
            valid=[p for p in selected if scores[p['pair_id']][a] is not None]
            labels=[int(p['category']==category) for p in valid]
            pooled[c][a]={'auc':float(roc_auc_score(labels,[scores[p['pair_id']][a] for p in valid])) if len(set(labels))==2 else None,
                         'n_positive':sum(labels),'n_negative':len(labels)-sum(labels)}
    noise={}
    for a in ['B768']+C_ARMS+D_ARMS:
        baseline=[scores[p['pair_id']][a] for p in rows if p['category']=='T1' or (p['category']=='T3' and p['strength']=='word')]
        baseline=[v for v in baseline if v is not None];p95=float(np.percentile(baseline,95))
        noise[a]={'n':len(baseline),'mean':float(np.mean(baseline)),'p50':float(np.median(baseline)),'p95':p95,'positive_above_p95':{}}
        for c in CONTRASTS:
            category,strength=c.split('-');v=[scores[p['pair_id']][a] for p in rows if p['category']==category and p['strength']==strength and scores[p['pair_id']][a] is not None]
            noise[a]['positive_above_p95'][c]=float(np.mean(np.array(v)>p95)) if v else None
    docrows=read_jsonl(out/'docset-scores.jsonl');docmetrics={}
    for a in C_ARMS+D_ARMS:
        docmetrics[a]={}
        for agg in ('max','mean'):
            eligible=[d for d in docrows if d[f'{a}_{agg}'] is not None]
            docmetrics[a][agg+'_auc']=float(roc_auc_score([d['label'] for d in eligible],[d[f'{a}_{agg}'] for d in eligible])) if len({d['label'] for d in eligible})==2 else None
        for label,name in ((1,'positive'),(0,'negative')):
            values=[d[f'{a}_trigger'] for d in docrows if d['label']==label and d[f'{a}_trigger'] is not None]
            docmetrics[a][name+'_any_paragraph_trigger']=float(np.mean(values)) if values else None
        docmetrics[a]['criterion_met_exploratory']=bool(docmetrics[a]['positive_any_paragraph_trigger']<.30 and max(docmetrics[a]['max_auc'],docmetrics[a]['mean_auc'])>=.80)
    hypotheses={'H1':{},'H2':{},'H3':{},'H4':{},'H5':primary['T5-word']['R']['auc']>=.95,'H6':{a:m['criterion_met_exploratory'] for a,m in docmetrics.items()},'H7':{'llm_comparison':'not run','skeleton_ranges':{}}}
    ablations={}
    for p in PREFIXES:
        for c in ('T6-word','T7-word'):
            same,alt,cross=[primary[c][f'C_{s}_{p}']['auc'] for s in SETS]
            key=f'{c}/{p}';relative=cross>=same-.10;absolute=cross<=.60
            ablations[key]={'same':same,'alt':alt,'xlang':cross,'same_minus_xlang':same-cross,'same_minus_alt':same-alt,'relative_criterion':relative,'absolute_low_criterion':absolute,'criteria_conflict':relative and absolute}
            hypotheses['H1'][key]=relative;hypotheses['H2'][key]=min(same,cross)<=alt<=max(same,cross)
    for s in SETS:
        hypotheses['H3'][s]=all(primary[c][f'D2_{s}_paired']['auc']>=.85 for c in ('T8-sentence','T8-paragraph'))
        hypotheses['H4'][s]=all(primary[c][f'D2_{s}_single']['auc']>=.80 for c in ('T6-word','T7-word','T8-sentence','T8-paragraph'))
    for a in C_ARMS:
        hypotheses['H7']['skeleton_ranges'][a]={c:max(skeletons[sk][c][a]['auc'] for sk in skeletons)-min(skeletons[sk][c][a]['auc'] for sk in skeletons) for c in ('T6-word','T7-word','T8-sentence','T8-paragraph')}
    metrics={'primary':primary,'by_language':languages,'by_skeleton':skeletons,'by_generator':{'rule':primary,'llm':None},'T8_with_ambiguous_T9_assumed_negative':t9,'pooled_secondary':pooled,
             'noise':noise,'docsets':docmetrics,'ablations':ablations,'hypotheses':hypotheses}
    (out/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
    # Correct the interpretation of v1 using its own fixed scores, without rerunning.
    oldrows=read_jsonl('data/synthetic-v1/pairs.jsonl');oldscore={r['pair_id']:r for r in read_jsonl('results/synthetic-v1/scores.jsonl')};v1={}
    for a in ('A','B768','C_classification','C_search_query','D_NLI'):
        selected=[p for p in oldrows if p['category'] in ('T4','T5')]
        v1[a]={'T5_vs_T4_auc':float(roc_auc_score([p['label'] for p in selected],[oldscore[p['pair_id']][a] for p in selected])),
               'T4_mean':float(np.mean([oldscore[p['pair_id']][a] for p in selected if p['category']=='T4'])),
               'T5_mean':float(np.mean([oldscore[p['pair_id']][a] for p in selected if p['category']=='T5']))}
    (out/'v1-date-reanalysis.json').write_text(json.dumps(v1,indent=2)+'\n')
    lines=['# v0.2 合成試驗結果','',f"在合成骨架內：{len(rows)} 組比較、{input_manifest['n_bases']} 段底稿、40 對文件集；所有資料由規則產生，Gemini 呼叫 0 次。",'',
           '本輪完成 A、B768、C 三組標籤 × 兩種前綴、D1、D2 三組、R 與固定組合。不是正式真實文件 Phase 2，也沒有獨立 LLM 覆核。', '',
           '## 評估邊界','',
           '- 主表以同底稿專屬負例計算 AUROC；完整 JSON 另列逐對勝率（平手計 0.5）、中英分層、骨架分層、各格樣本數。AUROC 是配對負例池的排序指標，不是準確率。',
           '- T8 sentence 主表只用確認為良性的 T3；另列規格要求的 T3+T9 敏感度分析，該分析把原本不確定的 T9 當負例，不能視為已驗證標註。',
           '- C-same 依 §4 刻意允許詞彙重疊；C-alt 對擾動詞表零重疊。規格 §3「所有標籤均不得重疊」與 §4 衝突，採 §4 的實驗定義。這個檢查不等於所有上下文詞彙都不重疊。',
           '- T10 使用先寫死的合成政策：日期順延、等客戶確認、換負責人三者同時出現才進入待審狀態。政策存在 metadata、未輸入模型；不是雙 prompt 確認的語意狀態，H6 僅探索。',
           '- 五個骨架仍共用短事實片語與有限 slots。沒有 LLM 改寫；跨骨架分數不能排除模板指紋。',
           '- T8 與 T3 只匹配底稿及名義強度：正例是新增，負例是改述／重排，未等化編輯操作或字數。日期亦未反平衡不同數字；詳見 data-audit.md。',
           '- C/D2 paired 成功不代表不需 old；只有 single 分數能回答該問題。相對門檻與絕對低分門檻若衝突，不做「語意／詞彙」因果斷言。',
           '- 沒有調 B、溫度、標籤、擾動詞或組合。T7/T10 不用來選設定；arm AUROC 相差 <0.05 按規格視為平手。','',
           '## 主表：同底稿專屬負例 AUROC','']
    lines+=table(primary,['A','B768','D1']+C_ARMS)
    lines+=['']+table(primary,D_ARMS+['R'])
    lines+=['','## 固定組合：max(R, D2_single)','']+table(primary,COMBOS,('T5-word','T6-word','T8-sentence'))
    lines+=['','## Q1、Q2：標籤用詞與語言','', '| 配對／前綴 | same | alt | xlang | same−xlang | same−alt | H1 | H2 |','|---|---|---|---|---|---|---|---|']
    for k,v in ablations.items():lines.append('| '+k+' | '+' | '.join(fmt(v[x]) for x in ('same','alt','xlang','same_minus_xlang','same_minus_alt'))+f" | {hypotheses['H1'][k]} | {hypotheses['H2'][k]} |")
    lines+=['','相對條件通過只是在這批資料中對換標籤語言的穩定性證據，不能單獨證明模型的因果機制。中英分開結果如下。']
    for lang in ('zh','en'):lines+=['',f'### {lang}','']+table(languages[lang],C_ARMS+D_ARMS,('T6-word','T7-word','T8-sentence'))
    lines+=['','## Q3：標籤 NLI 與 H3/H4','',f"H3（T8 paired ≥0.85，sentence 與 paragraph 均需通過）：`{json.dumps(hypotheses['H3'])}`。",f"H4（T6/T7 word、T8 sentence/paragraph 的 single 均 ≥0.80）：`{json.dumps(hypotheses['H4'])}`。",'',
            '以上僅使用本輪 rule 標註；不包含前文已存在風險但狀態未變、風險解除等完整反例，不能據此主張一般漂移偵測可以拿掉 old。', '',
            '## Q4：T10 與 H6（探索性政策任務）','', '| arm | max AUROC | mean AUROC | 正例任一段觸發率 | 負例任一段觸發率 | 數值門檻 |','|---|---|---|---|---|---|']
    for a,m in docmetrics.items():lines.append(f"| {a} | {fmt(m['max_auc'])} | {fmt(m['mean_auc'])} | {fmt(m['positive_any_paragraph_trigger'])} | {fmt(m['negative_any_paragraph_trigger'])} | {m['criterion_met_exploratory']} |")
    lines+=['','觸發門檻固定為各 arm 在全部 T3 的 p95。這是同一合成資料內的描述性分位數，沒有獨立校準集。D2 single 的 max 對應規格要求的三段單邊最大分數。','',
            '## Q5：日期與 H5','',f"R 的 T5/T4 AUROC = {fmt(primary['T5-word']['R']['auc'])}，抽取缺漏 {60-primary['T5-word']['R']['n_positive']} 個正例；H5 = {hypotheses['H5']}。僅涵蓋此版 ISO 日期與固定欄位文字，其他格式未證明。",'',
            f"v1 原始分數重分析：D1 的 T5/T4 AUROC = {v1['D_NLI']['T5_vs_T4_auc']:.3f}，T4 mean = {v1['D_NLI']['T4_mean']:.3f}、T5 mean = {v1['D_NLI']['T5_mean']:.3f}。原先合併負例 AUROC 不能支持跨截止日推理的結論。完整重算見 v1-date-reanalysis.json；此處是同類負例比較，未宣稱 v1 的底稿逐對匹配。",'',
            '## Q6：五骨架與 H7','', '下表是各骨架 AUROC 最大值減最小值；<0.10 是規格門檻。LLM vs rule 未執行，因此 H7 完整條件無法判定。','', '| arm | T6 word | T7 word | T8 sentence | T8 paragraph |','|---|---|---|---|---|']
    for a,m in hypotheses['H7']['skeleton_ranges'].items():lines.append('| '+a+' | '+' | '.join(fmt(m[c]) for c in ('T6-word','T7-word','T8-sentence','T8-paragraph'))+' |')
    lines+=['','## Q7：良性改動底線','', '| arm | mean | p50 | p95 | T6 word > p95 | T7 word > p95 | T8 sentence > p95 |','|---|---|---|---|---|---|---|']
    for a,m in noise.items():lines.append('| '+a+' | '+' | '.join(fmt(m[k]) for k in ('mean','p50','p95'))+' | '+' | '.join(fmt(m['positive_above_p95'][c]) for c in ('T6-word','T7-word','T8-sentence'))+' |')
    lines+=['','底線為 T1 + T3-word，共 360 筆；T0 僅重編碼一次檢查浮點決定性，見 determinism.json。','',
            '## v1 日期前提的核對','',
            'v0.2 文件稱「三個語意 arm 全盲」，但 v1 實際分數不支持此概括。以下重算使用各類原始資料；A/B/C 的高分也不能證明有日期推理，因 v1 日期負例改一字、正例改三字，編輯幅度未受控。','',
            '| v1 arm | T5/T4 AUROC | T4 mean | T5 mean |','|---|---|---|---|']
    for a,m in v1.items():lines.append(f"| {a} | {fmt(m['T5_vs_T4_auc'])} | {fmt(m['T4_mean'])} | {fmt(m['T5_mean'])} |")
    lines+=['','## T9 敏感度分析','', '| arm | T3 confirmed | T3+T9 assumed negative |','|---|---|---|']
    for a in ARMS:lines.append(f"| {a} | {fmt(primary['T8-sentence'][a]['auc'])} | {fmt(t9[a]['auc'])} |")
    lines+=['','## 合併負例對照（次要）','', '這張表沿用 v1 的 T1+T2+T3+T4 合併負例，不能取代上方主表。','']+table(pooled,['A','B768','D1']+C_ARMS+D_ARMS)
    lines+=['','## 檔案與未跑項目','', '- `metrics.json`：完整分層、逐對勝率、分數門檻及 H1–H7 數值。','- `extremes.jsonl`：每個 T0–T10 類別 5 筆極端例句，按 C-same classification 排序取兩端；這是診斷抽查，不是獨立驗證。',
            '- `manifest.json`：模型 revision、環境版本、輸入與評分程式 SHA256；`data/synthetic-v2/analysis-plan.json` 保存評分前的判讀方式。',
            '- 未跑：Gemini 生成與覆核、E、B2、D2-DM。J 屬後續 v0.2.1，分開記錄。','']
    (out/'report.md').write_text('\n'.join(lines))
    summary=['# v0.2 合成試驗摘要','', '在合成骨架內，完成 420 段底稿、1,690 組比較、40 對文件集；全部規則生成，沒有 Gemini 呼叫或獨立標註。','']
    summary+=table(primary,['B768','C_same_classification','C_alt_classification','C_xlang_classification','D1','D2_same_paired','D2_same_single','R'],('T5-word','T6-word','T7-word','T8-sentence','T8-paragraph'))
    summary+=['',f"H1（兩種前綴、T6/T7 word）數值條件：{sum(hypotheses['H1'].values())}/4 通過；H2：{sum(hypotheses['H2'].values())}/4 通過。",f"H3：{json.dumps(hypotheses['H3'])}；H4：{json.dumps(hypotheses['H4'])}；H5：{hypotheses['H5']}。",'',
              'H6 只有合成政策任務結果；H7 缺少 LLM 改寫對照。所有推論僅限本批模板；T8 主表排除不確定的 T9，完整報告另有含 T9 的敏感度表。','',
              '配對 D2 的高 AUROC 不等於單邊偵測已經成立；即使 single 在本資料高分，也未測「原本就處於風險但本次未變」等必要反例。','',
              '[完整報告](report.md) · [配對與分層數值](metrics.json) · [圖](fig/paired-auroc.png) · [v1 日期重分析](v1-date-reanalysis.json)','']
    (out/'summary.md').write_text('\n'.join(summary))
    extremes=[]
    for cat in sorted({p['category'] for p in rows},key=lambda s:int(s[1:])):
        chosen=sorted([p for p in rows if p['category']==cat],key=lambda p:(scores[p['pair_id']]['C_same_classification'],p['pair_id']))
        for p in chosen[:3]+chosen[-2:]:extremes.append({**p,'scores':scores[p['pair_id']],'audit_status':'diagnostic extremes only; not independent adjudication'})
    write_jsonl(out/'extremes.jsonl',extremes)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir=out/'fig';figdir.mkdir(exist_ok=True)
    plotarms=['A','B768','D1']+C_ARMS+D_ARMS
    fig,ax=plt.subplots(figsize=(15,5));matrix=np.array([[primary[c][a]['auc'] for a in plotarms] for c in CONTRASTS])
    im=ax.imshow(matrix,vmin=0,vmax=1,cmap='viridis',aspect='auto');ax.set_xticks(range(len(plotarms)),[a.replace('classification','class').replace('search_query','search') for a in plotarms],rotation=55,ha='right');ax.set_yticks(range(len(CONTRASTS)),CONTRASTS)
    for i in range(len(CONTRASTS)):
        for j in range(len(plotarms)):ax.text(j,i,f'{matrix[i,j]:.2f}',ha='center',va='center',fontsize=8,color='black' if matrix[i,j]>.65 else 'white')
    ax.set_title('Synthetic-v2: matched-base controls, AUROC (rule generator only)');fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(figdir/'paired-auroc.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5));names=list(docmetrics);x=np.arange(len(names))
    ax.bar(x-.2,[docmetrics[a]['max_auc'] for a in names],.4,label='Docset max AUROC');ax.bar(x+.2,[docmetrics[a]['positive_any_paragraph_trigger'] for a in names],.4,label='Positive any-paragraph trigger');ax.set_xticks(x,[a.replace('classification','class').replace('search_query','search') for a in names],rotation=60,ha='right');ax.set_ylim(0,1.05);ax.legend();ax.set_title('T10: stipulated synthetic policy; no independent adjudication');fig.tight_layout();fig.savefig(figdir/'docsets.png',dpi=160);plt.close(fig)
    validation={'n_scores':len(results),'duplicate_ids':False,'all_scores_finite_or_null':True,'data_hashes_valid':True,'n_r_missing_T4_T5':sum(scores[p['pair_id']]['R'] is None for p in rows if p['category'] in ('T4','T5')),
                'scores_sha256':digest(out/'scores.jsonl'),'report_sha256':digest(out/'report.md')}
    (out/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(hypotheses,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

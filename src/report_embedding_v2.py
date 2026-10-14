"""Publish completed embedding/R results while the independent NLI stage runs."""
import json
from pathlib import Path
import numpy as np
from .common import read_jsonl,digest
from .report_v2 import matched,table,CONTRASTS,C_ARMS
from .run_v2 import verify_data


def main():
    data=Path('data/synthetic-v2');out=Path('results/synthetic-v2');verify_data(data)
    rows=read_jsonl(data/'pairs.jsonl');scores={r['pair_id']:r for r in read_jsonl(out/'embedding-scores.jsonl')}
    arms=['A','B768']+C_ARMS+['R']
    metrics={c:{a:matched(rows,scores,c,a) for a in arms} for c in CONTRASTS}
    lines=['# v0.2 已完成的 EG2／規則結果','',
           '這份表只涵蓋已完成的 A、B、C、R。NLI 與 J 請另看完整報告，勿把尚未完成的欄位當成零分。所有結論限於本批合成骨架。','']
    lines+=table(metrics,arms)
    lines+=['','T6/T7 word 使用同底稿 T3-word；T8 sentence 主表使用 T3-sentence，不包含不確定 T9。','',
            'C 是四類機率分布的 cosine 距離，AUROC 接近 1 不表示四分類幾乎全對。下表另列正例 argmax 改變比例。','',
            '| 配對 | '+' | '.join(C_ARMS)+' |','|---|'+'---|'*len(C_ARMS)]
    for c in CONTRASTS:
        category,strength=c.split('-');selected=[p for p in rows if p['category']==category and p['strength']==strength]
        rates=[float(np.mean([scores[p['pair_id']][a+'_argmax'] for p in selected])) for a in C_ARMS]
        lines.append('| '+c+' | '+' | '.join(f'{r:.3f}' for r in rates)+' |')
    lines+=['','目前這批資料的跨語言／異詞標籤沒有造成 T6/T7 word 明顯退步；這是描述性結果，不是模型因果機制的證明。',
            '本輪與 v1 的控制組和模板都不同，AUROC 升降不能解讀成模型能力改變。T3-word 僅改中性記錄詞，未完整涵蓋狀態句的良性改述。',
            '日期正負例均只改一字，但日期數字未反平衡；B 的日期分數仍可能受 token 距離影響。完整資料限制見 [覆核紀錄](data-audit.md)。','']
    (out/'embedding-summary.md').write_text('\n'.join(lines))
    (out/'embedding-metrics.json').write_text(json.dumps({'score_sha256':digest(out/'embedding-scores.jsonl'),'data_manifest_sha256':digest(data/'manifest.json'),'metrics':metrics},ensure_ascii=False,indent=2)+'\n')
    print('\n'.join(lines[:14]))

if __name__=='__main__':main()

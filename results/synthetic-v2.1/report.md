# v0.2.1：jevlike J arm 合成試驗

依 `main@fb62b10` 的規格追加 J。資料、標籤與配對關係沿用已凍結的 synthetic-v2；沒有新增 Gemini 呼叫。

目前模型狀態：E2B=complete；E4B=running。未完成的品質指標不填零。

主表 AUROC 是同底稿專屬負例池的排序指標，不是逐對勝率或分類準確率；中英分層另列。

J 使用 `jevlike@9838918533cf3d88dc975ef19d38122b07df47f7` 的既有四選一／布林題介面，未改 prompt 模板。llama.cpp 固定 b11371（99b95488），CPU、4 threads、Q8_0。

## 主表：專屬負例配對 AUROC

| 配對 | C-alt class | D2-alt paired | D2-alt single | J-E2B single | J-E4B single | R |
|---|---|---|---|---|---|---|
| T5-word | 0.317 | 0.642 | 0.512 | 0.689 | — | 1.000 |
| T6-word | 0.997 | 0.998 | 0.922 | 0.889 | — | — |
| T6-sentence | 1.000 | 1.000 | 0.990 | 0.998 | — | — |
| T7-word | 0.999 | 1.000 | 0.966 | 1.000 | — | — |
| T7-sentence | 1.000 | 1.000 | 0.996 | 1.000 | — | — |
| T8-sentence | 1.000 | 0.985 | 0.951 | 1.000 | — | — |
| T8-paragraph | 0.999 | 0.959 | 1.000 | 1.000 | — | — |

J 缺少候選選項時保留 null。不同 arm 若有效樣本不同，主表不能直接比較；下方提供每格正／負樣本數及 J／D2 共同有效樣本上的差。所有結論限於合成骨架內。

## E2B

狀態：complete。
單邊缺值 0/1230；配對缺值 0/1230。另有 460 筆不屬 J 配對評估範圍（T0/T1/T2、T10 個別段落），未跑且保留 null；T10 改評全部 80 組 concat。權重 5.05 GB，revision `0314792d7f1f7e229411f620751375812bb9faf2`。

| 配對 | single AUROC (正/負) | paired AUROC (正/負) | 共同樣本 J−D2-alt single |
|---|---|---|---|
| T5-word | 0.689 (60/60) | 1.000 (60/60) | 0.177 |
| T6-word | 0.889 (300/300) | 0.994 (300/300) | -0.032 |
| T6-sentence | 0.998 (50/50) | 1.000 (50/50) | 0.008 |
| T7-word | 1.000 (60/60) | 1.000 (60/60) | 0.034 |
| T7-sentence | 1.000 (60/60) | 1.000 (60/60) | 0.004 |
| T8-sentence | 1.000 (60/60) | 1.000 (60/60) | 0.049 |
| T8-paragraph | 1.000 (60/60) | 1.000 (60/60) | 0.000 |

T10 三段 new concat：AUROC 0.772，有效正／負 40/40。此為合成政策任務，未經獨立判讀。

### H8–H11

數值門檻與完整覆蓋分開記錄；只在兩者均通過時才可說這批資料滿足該假說。H8 的正式門檻以 E2B 為主，E4B 是後續能力比較。

```json
{
  "H8_numeric": true,
  "H8_complete": true,
  "H9_numeric": false,
  "H9_complete": true,
  "H10_tie_on_common_cases": true,
  "H10_J_stronger_all": false,
  "H11_numeric_exploratory": false,
  "H11_complete": true
}
```

H10 不平手可能是 J 較強、較弱或各類互有優劣；不能把「不平手」直接解讀為 J 較強，也不能從本資料決定正式架構。

### zh single AUROC

| 配對 | AUROC | 正/負 |
|---|---|---|
| T5-word | 0.788 | 30/30 |
| T6-word | 0.942 | 150/150 |
| T6-sentence | 1.000 | 25/25 |
| T7-word | 1.000 | 30/30 |
| T7-sentence | 1.000 | 30/30 |
| T8-sentence | 1.000 | 30/30 |
| T8-paragraph | 1.000 | 30/30 |

### en single AUROC

| 配對 | AUROC | 正/負 |
|---|---|---|
| T5-word | 0.858 | 30/30 |
| T6-word | 0.961 | 150/150 |
| T6-sentence | 1.000 | 25/25 |
| T7-word | 1.000 | 30/30 |
| T7-sentence | 1.000 | 30/30 |
| T8-sentence | 1.000 | 30/30 |
| T8-paragraph | 1.000 | 30/30 |

## E4B

狀態：running。
完整品質評估尚未完成；100 筆成本測試已完成，另列。

## 成本：同一台 CPU、同一批 100 筆

| arm | 平均端到端 ms | p95 ms | 平均 prefill ms | 平均輸入 tokens | 模型 | prewarm 後可否固定預算 |
|---|---|---|---|---|---|---|
| C_alt_classification | 240.918 | 305.978 | — | 72.610 | 271.0M / float32 | 標籤／old 已預算；new embedding 仍隨長度變動 |
| D2_alt_single | 435.707 | 605.077 | — | 287.520 | 278.8M / float32 | 4 組 premise/hypothesis，單批 forward；仍隨長度變動 |
| J_e2b | 7235.885 | 10330.065 | 7208.342 | 190.780 | 5.05 GB / Q8_0 | 每題一次 prefill；隨輸入長度變動 |
| J_e4b | 16078.051 | 22015.817 | 16014.887 | 190.780 | 8.19 GB / Q8_0 | 每題一次 prefill；隨輸入長度變動 |

所有 arm 先做一次不計時 warmup，再逐段測量；J 的 100 筆成本測試關閉 prompt cache。這 100 筆預測沿用於品質評估，其餘品質推論啟用既有 prefix cache；兩者逐題標記，不能把品質推論的延遲混入成本表。D2 四個標籤以一批計算，token 數是四組總和；J 題目包含標籤與模板，token 數自然不同。EG2 的 old 向量與 label 已預算，時間包含 new embedding；僅有既有向量的投影運算可視為固定維度成本。

## 限制與可追溯性

- J 單邊分類衡量目前是否為風險狀態，不等於一般狀態漂移。資料沒有完整涵蓋「原本已卡關但本次未變」或解除風險的反例。
- 日期跨期正例只改日期，原文「進度領先」仍保留，形成文字敘述與日期值之間的衝突；模型對此的表現不能單獨代表一般日期推理能力。
- T10 使用三個信號同時成立才待審的人工政策，沒有兩個獨立 prompt 判讀，政策也沒送入模型；H11 只能探索。
- `summary.json` 保存中英分層、共同有效樣本比較、候選 option mass 與成本分布；各模型 `predictions.jsonl` 保存每題延遲、token、原始字母 logprob、缺選項及 prompt hash。
- `data/synthetic-v2.1/analysis-plan.json` 保存評分前凍結的題目、標籤順序、模型 revision、100 筆 benchmark IDs。模型 SHA256、引擎 SHA256 與程式 SHA256 見各模型 manifest。

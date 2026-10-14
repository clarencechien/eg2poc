# EG2 狀態漂移實驗報表

**僅為測試程式的人工 fixture；不是正式實驗，禁止用來判定 H1–H7。**

執行狀態：failed。樣本數：20。

D_NLI 表示 NLI 替代，並非 Decision Maker。E 僅在抽樣子集計分；各格括號為正例／負例數，不可直接與全量結果排序。
T9 不納入 AUROC；固定負例為 T1+T2+T3+T4。缺少一個 class 不計算 AUROC。

## 覆蓋缺口

- base count 2; target 150–200
- document count 1; target ≥20
- Some bases lack real repository provenance
- zh bases below 75
- en bases below 75
- T1/zh below 30 pairs
- T1/en below 30 pairs
- T2/zh below 30 pairs
- T2/en below 30 pairs
- T3/zh below 30 pairs
- T3/en below 30 pairs
- T4/zh below 30 pairs
- T4/en below 30 pairs
- T5/zh below 30 pairs
- T5/en below 30 pairs
- T6/zh below 30 pairs
- T6/en below 30 pairs
- T7/zh below 30 pairs
- T7/en below 30 pairs
- T8/zh below 30 pairs
- T8/en below 30 pairs
- T0 below 100 pairs
- T6-zh-沒有 below 15 pairs
- T6-zh-不再 below 15 pairs
- T6-zh-尚未 below 15 pairs
- T6-zh-取消 below 15 pairs
- T6-zh-暫停 below 15 pairs
- Missing T3/word
- Missing T3/paragraph
- Missing T6/word
- Missing T6/paragraph
- Missing T8/word
- Missing T8/paragraph
- T5 rule/llm not balanced: [2, 0]
- T6 rule/llm not balanced: [2, 0]
- T7 rule/llm not balanced: [2, 0]

## AUROC：all

| 類別 | A | B768 | B256 | B2 | C_classification | C_search_query | D_NLI | E |
|---|---|---|---|---|---|---|---|---|
| T5 | 0.500 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6 | 0.312 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-沒有 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-不再 | 0.375 (1/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-尚未 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-取消 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-暫停 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-en | 0.250 (1/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T7 | 0.438 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T8 | 0.500 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |

## AUROC：rule

| 類別 | A | B768 | B256 | B2 | C_classification | C_search_query | D_NLI | E |
|---|---|---|---|---|---|---|---|---|
| T5 | 0.500 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6 | 0.312 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-沒有 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-不再 | 0.375 (1/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-尚未 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-取消 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-暫停 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-en | 0.250 (1/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T7 | 0.438 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T8 | 0.500 (2/8) | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |

## AUROC：llm

| 類別 | A | B768 | B256 | B2 | C_classification | C_search_query | D_NLI | E |
|---|---|---|---|---|---|---|---|---|
| T5 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-沒有 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-不再 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-尚未 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-取消 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-暫停 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-en | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T7 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T8 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |

## Q6 雜訊底線

| run | batch | n | mean | std | p95 | max |
|---|---|---|---|---|---|---|
| 未跑 | — | — | — | — | — | — |

## Q7 靈敏度

| 類別 | strength | n | B mean | B p50 | 超過 noise p95 比例 |
|---|---|---|---|---|---|
| T3 | word | 0 | 未跑 | 未跑 | 未跑 |
| T3 | sentence | 0 | 未跑 | 未跑 | 未跑 |
| T3 | paragraph | 0 | 未跑 | 未跑 | 未跑 |
| T6 | word | 0 | 未跑 | 未跑 | 未跑 |
| T6 | sentence | 0 | 未跑 | 未跑 | 未跑 |
| T6 | paragraph | 0 | 未跑 | 未跑 | 未跑 |
| T8 | word | 0 | 未跑 | 未跑 | 未跑 |
| T8 | sentence | 0 | 未跑 | 未跑 | 未跑 |
| T8 | paragraph | 0 | 未跑 | 未跑 | 未跑 |

## 每類／arm 最極端樣本（最多 5 筆；需人工覆核）

### T1 / A

- `fixture-zh:T1:rule:0` score=0.066667
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。  "
- `fixture-en:T1:rule:0` score=0.023810
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10.  "
### T2 / A

- `fixture-en:T2:rule:0` score=0.619048
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The deadline is May 31 and shipment is planned for May 10. The delivery is on track."
- `fixture-zh:T2:rule:0` score=0.600000
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "截止日期為五月三十一日，預計五月十日出貨。交付進度符合計畫。"
### T3 / A

- `fixture-en:T3:rule:0` score=0.892857
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "Delivery remains on schedule, with shipment planned for May 10 ahead of the May 31 deadline."
- `fixture-zh:T3:rule:0` score=0.566667
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "目前交付仍按計畫進行，預計在五月三十一日截止前，於五月十日出貨。"
### T4 / A

- `fixture-zh:T4:rule:0` score=0.066667
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "交付進度符合計畫。截止日期為五月三十一日，預計五月二十五日出貨。"
- `fixture-en:T4:rule:0` score=0.023810
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The delivery is on track. The deadline is May 31 and shipment is planned for May 25."
### T5 / A

- `fixture-en:T5:rule:0` score=0.261905
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The delivery is delayed. The deadline is May 31 and shipment is now planned for September 30."
- `fixture-zh:T5:rule:0` score=0.266667
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "交付進度已延後。截止日期為五月三十一日，目前預計九月三十日出貨。"
### T6 / A

- `fixture-en:T6:rule:0` score=0.047619
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The delivery is not on track. The deadline is May 31 and shipment is planned for May 10."
- `fixture-zh:T6:rule:0` score=0.066667
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "交付進度不再符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
### T7 / A

- `fixture-zh:T7:rule:0` score=0.066667
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "交付進度落後計畫。截止日期為五月三十一日，預計五月十日出貨。"
- `fixture-en:T7:rule:0` score=0.166667
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The delivery is behind schedule. The deadline is May 31 and shipment is planned for May 10."
### T8 / A

- `fixture-zh:T8:rule:0` score=0.533333
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。新增的相依服務故障目前阻礙出貨。"
- `fixture-en:T8:rule:0` score=0.547619
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10. A new dependency failure now blocks shipment."
### T9 / A

- `fixture-zh:T9:rule:0` score=0.300000
  - old: "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。"
  - new: "截止日期為五月三十一日，預計五月十日出貨。"
- `fixture-en:T9:rule:0` score=0.309524
  - old: "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."
  - new: "The deadline is May 31 and shipment is planned for May 10."

## Q1–Q8

- Q1: 正式實驗未跑；T8 與固定負例的 B AUROC 見主表；不將 T1/T2/T3/T4 當正例。
- Q2: 正式實驗未跑；T6/T7 的 B AUROC 見主表；有實際 B 分數才產生分布圖。
- Q3: 正式實驗未跑；兩種 C prefix 均列出；C−B 差異見下表。不用 T7 選 prefix。
- Q4: 正式實驗未跑；D_NLI T6/T7 見主表；無法外推至 Decision Maker。
- Q5: 正式實驗未跑；五種中文形態各列主表；不能只由 AUROC 宣稱『完全看不見』。
- Q6: 正式實驗未跑；雜訊表列 batch size／順序改變後的三次量測；未跑不填零。
- Q7: 正式實驗未跑；靈敏度表只使用實測 B 距離；圖只在有數據時產生。
- Q8: 正式實驗未跑；T7 是 holdout，主表固定呈現；差距 <0.05 視為打平。

| category | C classification − B | C search query − B |
|---|---|---|
| T5 | 未跑 | 未跑 |
| T6 | 未跑 | 未跑 |
| T6-zh-沒有 | 未跑 | 未跑 |
| T6-zh-不再 | 未跑 | 未跑 |
| T6-zh-尚未 | 未跑 | 未跑 |
| T6-zh-取消 | 未跑 | 未跑 |
| T6-zh-暫停 | 未跑 | 未跑 |
| T6-en | 未跑 | 未跑 |
| T7 | 未跑 | 未跑 |
| T8 | 未跑 | 未跑 |

## H1–H7

假說定義以 docs/protocol-v0.1.md 為準。數量不足或 diagnostic 時禁止給出保留／淘汰結論。

- H1: 無法判定（diagnostic；資料覆蓋不足；缺少：B768）。
- H2: 無法判定（diagnostic；資料覆蓋不足；缺少：B768）。
- H3: 無法判定（diagnostic；資料覆蓋不足；缺少：B768, C_classification, C_search_query, D_NLI）。
- H4: 無法判定（diagnostic；資料覆蓋不足；缺少：D_NLI）。
- H5: 無法判定（diagnostic；資料覆蓋不足；缺少：B768, B256, B2, C_classification, C_search_query, D_NLI, E）。
- H6: 無法判定（diagnostic；資料覆蓋不足；缺少：B768, C_classification, C_search_query, D_NLI）。
- H7: 無法判定（diagnostic；資料覆蓋不足；缺少：B768, C_classification, C_search_query, D_NLI）。

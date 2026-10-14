# v0.2 合成試驗結果

在合成骨架內：1690 組比較、420 段底稿、40 對文件集；所有資料由規則產生，Gemini 呼叫 0 次。

本輪完成 A、B768、C 三組標籤 × 兩種前綴、D1、D2 三組、R 與固定組合。不是正式真實文件 Phase 2，也沒有獨立 LLM 覆核。

## 評估邊界

- 主表以同底稿專屬負例計算 AUROC；完整 JSON 另列逐對勝率（平手計 0.5）、中英分層、骨架分層、各格樣本數。AUROC 是配對負例池的排序指標，不是準確率。
- T8 sentence 主表只用確認為良性的 T3；另列規格要求的 T3+T9 敏感度分析，該分析把原本不確定的 T9 當負例，不能視為已驗證標註。
- C-same 依 §4 刻意允許詞彙重疊；C-alt 對擾動詞表零重疊。規格 §3「所有標籤均不得重疊」與 §4 衝突，採 §4 的實驗定義。這個檢查不等於所有上下文詞彙都不重疊。
- T10 使用先寫死的合成政策：日期順延、等客戶確認、換負責人三者同時出現才進入待審狀態。政策存在 metadata、未輸入模型；不是雙 prompt 確認的語意狀態，H6 僅探索。
- 五個骨架仍共用短事實片語與有限 slots。沒有 LLM 改寫；跨骨架分數不能排除模板指紋。
- T8 與 T3 只匹配底稿及名義強度：正例是新增，負例是改述／重排，未等化編輯操作或字數。日期亦未反平衡不同數字；詳見 data-audit.md。
- C/D2 paired 成功不代表不需 old；只有 single 分數能回答該問題。相對門檻與絕對低分門檻若衝突，不做「語意／詞彙」因果斷言。
- 沒有調 B、溫度、標籤、擾動詞或組合。T7/T10 不用來選設定；arm AUROC 相差 <0.05 按規格視為平手。

## 主表：同底稿專屬負例 AUROC

| 配對 | A | B768 | D1 | C_same_classification | C_same_search_query | C_alt_classification | C_alt_search_query | C_xlang_classification | C_xlang_search_query |
|---|---|---|---|---|---|---|---|---|---|
| T5-word | 0.500 | 0.879 | 0.536 | 0.243 | 0.102 | 0.317 | 0.643 | 0.487 | 0.178 |
| T6-word | 0.539 | 0.851 | 1.000 | 0.994 | 0.991 | 0.997 | 0.989 | 0.999 | 0.994 |
| T6-sentence | 0.812 | 0.983 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.998 |
| T7-word | 0.660 | 0.942 | 1.000 | 0.999 | 1.000 | 0.999 | 1.000 | 1.000 | 1.000 |
| T7-sentence | 0.544 | 0.780 | 1.000 | 1.000 | 1.000 | 1.000 | 0.999 | 1.000 | 1.000 |
| T8-sentence | 0.972 | 0.930 | 1.000 | 1.000 | 1.000 | 1.000 | 0.993 | 1.000 | 1.000 |
| T8-paragraph | 0.571 | 0.455 | 0.725 | 1.000 | 1.000 | 0.999 | 0.962 | 1.000 | 0.958 |

| 配對 | D2_same_paired | D2_same_single | D2_alt_paired | D2_alt_single | D2_xlang_paired | D2_xlang_single | R |
|---|---|---|---|---|---|---|---|
| T5-word | 0.509 | 0.509 | 0.642 | 0.512 | 0.419 | 0.511 | 1.000 |
| T6-word | 0.996 | 0.833 | 0.998 | 0.922 | 0.998 | 0.875 | — |
| T6-sentence | 1.000 | 0.976 | 1.000 | 0.990 | 1.000 | 1.000 | — |
| T7-word | 1.000 | 0.873 | 1.000 | 0.966 | 1.000 | 0.924 | — |
| T7-sentence | 1.000 | 1.000 | 1.000 | 0.996 | 1.000 | 0.989 | — |
| T8-sentence | 0.999 | 0.881 | 0.985 | 0.951 | 1.000 | 0.922 | — |
| T8-paragraph | 0.999 | 1.000 | 0.959 | 1.000 | 1.000 | 1.000 | — |

### 副分數：正例 argmax 改變比例

分布距離 AUROC 高不等於四分類正確或 argmax 有改變；此表也不是分類準確率。

| 配對 | C_same_classification | C_alt_classification | C_xlang_classification | D2_same | D2_alt | D2_xlang |
|---|---|---|---|---|---|---|
| T5-word | 0.000 | 0.017 | 0.000 | 0.000 | 0.067 | 0.017 |
| T6-word | 0.020 | 0.227 | 0.000 | 0.297 | 0.543 | 0.407 |
| T6-sentence | 0.160 | 0.400 | 0.080 | 0.980 | 0.540 | 1.000 |
| T7-word | 0.033 | 0.367 | 0.050 | 0.967 | 0.550 | 0.867 |
| T7-sentence | 0.333 | 0.583 | 0.167 | 1.000 | 0.633 | 0.967 |
| T8-sentence | 0.350 | 0.300 | 0.000 | 0.417 | 0.417 | 0.467 |
| T8-paragraph | 0.717 | 0.567 | 0.317 | 1.000 | 0.417 | 0.917 |

## 固定組合：max(R, D2_single)

| 配對 | final_same | final_alt | final_xlang |
|---|---|---|---|
| T5-word | 1.000 | 1.000 | 1.000 |
| T6-word | 0.833 | 0.922 | 0.875 |
| T8-sentence | 0.881 | 0.951 | 0.922 |

## Q1、Q2：標籤用詞與語言

| 配對／前綴 | same | alt | xlang | same−xlang | same−alt | H1 | H2 |
|---|---|---|---|---|---|---|---|
| T6-word/classification | 0.994 | 0.997 | 0.999 | -0.005 | -0.003 | True | True |
| T7-word/classification | 0.999 | 0.999 | 1.000 | -0.001 | 0.000 | True | True |
| T6-word/search_query | 0.991 | 0.989 | 0.994 | -0.003 | 0.002 | True | False |
| T7-word/search_query | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | True | True |

相對條件通過只是在這批資料中對換標籤語言的穩定性證據，不能單獨證明模型的因果機制。中英分開結果如下。

### zh

| 配對 | C_same_classification | C_same_search_query | C_alt_classification | C_alt_search_query | C_xlang_classification | C_xlang_search_query | D2_same_paired | D2_same_single | D2_alt_paired | D2_alt_single | D2_xlang_paired | D2_xlang_single |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T6-word | 0.997 | 0.994 | 1.000 | 0.979 | 1.000 | 0.999 | 0.994 | 0.818 | 0.999 | 0.909 | 0.993 | 0.927 |
| T7-word | 0.998 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.788 | 1.000 | 1.000 | 1.000 | 1.000 |
| T8-sentence | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.978 | 1.000 | 0.938 |

### en

| 配對 | C_same_classification | C_same_search_query | C_alt_classification | C_alt_search_query | C_xlang_classification | C_xlang_search_query | D2_same_paired | D2_same_single | D2_alt_paired | D2_alt_single | D2_xlang_paired | D2_xlang_single |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T6-word | 0.999 | 0.995 | 0.996 | 0.999 | 1.000 | 0.991 | 1.000 | 0.957 | 0.998 | 0.982 | 1.000 | 0.820 |
| T7-word | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.979 | 1.000 | 1.000 | 1.000 | 0.744 |
| T8-sentence | 1.000 | 1.000 | 1.000 | 0.988 | 1.000 | 1.000 | 0.999 | 0.957 | 0.996 | 1.000 | 1.000 | 1.000 |

## Q3：標籤 NLI 與 H3/H4

H3（T8 paired ≥0.85，sentence 與 paragraph 均需通過）：`{"same": true, "alt": true, "xlang": true}`。
H4（T6/T7 word、T8 sentence/paragraph 的 single 均 ≥0.80）：`{"same": true, "alt": true, "xlang": true}`。

以上僅使用本輪 rule 標註；不包含前文已存在風險但狀態未變、風險解除等完整反例，不能據此主張一般漂移偵測可以拿掉 old。

## Q4：T10 與 H6（探索性政策任務）

| arm | max AUROC | mean AUROC | 正例任一段觸發率 | 負例任一段觸發率 | 數值門檻 |
|---|---|---|---|---|---|
| C_same_classification | 0.829 | 0.748 | 0.000 | 0.000 | True |
| C_same_search_query | 0.951 | 0.925 | 0.000 | 0.000 | True |
| C_alt_classification | 0.934 | 0.951 | 0.000 | 0.000 | True |
| C_alt_search_query | 0.971 | 0.974 | 0.000 | 0.000 | True |
| C_xlang_classification | 0.819 | 0.811 | 0.025 | 0.000 | True |
| C_xlang_search_query | 0.859 | 0.792 | 0.000 | 0.000 | True |
| D2_same_paired | 0.908 | 0.909 | 0.125 | 0.000 | True |
| D2_same_single | 0.545 | 0.581 | 0.150 | 0.125 | False |
| D2_alt_paired | 0.629 | 0.629 | 0.000 | 0.000 | False |
| D2_alt_single | 0.545 | 0.547 | 0.100 | 0.050 | False |
| D2_xlang_paired | 0.794 | 0.790 | 0.000 | 0.000 | False |
| D2_xlang_single | 0.610 | 0.580 | 0.425 | 0.150 | False |

觸發門檻固定為各 arm 在全部 T3 的 p95。這是同一合成資料內的描述性分位數，沒有獨立校準集。D2 single 的 max 對應規格要求的三段單邊最大分數。

## Q5：日期與 H5

R 的 T5/T4 AUROC = 1.000，抽取缺漏 0 個正例；H5 = True。僅涵蓋此版 ISO 日期與固定欄位文字，其他格式未證明。

v1 原始分數重分析：D1 的 T5/T4 AUROC = 0.485，T4 mean = 0.993、T5 mean = 0.990。原先合併負例 AUROC 不能支持跨截止日推理的結論。完整重算見 v1-date-reanalysis.json；此處是同類負例比較，未宣稱 v1 的底稿逐對匹配。

## Q6：五骨架與 H7

下表是各骨架 AUROC 最大值減最小值；<0.10 是規格門檻。LLM vs rule 未執行，因此 H7 完整條件無法判定。

| arm | T6 word | T7 word | T8 sentence | T8 paragraph |
|---|---|---|---|---|
| C_same_classification | 0.008 | 0.000 | 0.000 | 0.000 |
| C_same_search_query | 0.024 | 0.000 | 0.000 | 0.000 |
| C_alt_classification | 0.001 | 0.000 | 0.000 | 0.000 |
| C_alt_search_query | 0.064 | 0.000 | 0.076 | 0.097 |
| C_xlang_classification | 0.005 | 0.000 | 0.000 | 0.000 |
| C_xlang_search_query | 0.047 | 0.000 | 0.000 | 0.125 |

## Q7：良性改動底線

| arm | mean | p50 | p95 | T6 word > p95 | T7 word > p95 | T8 sentence > p95 |
|---|---|---|---|---|---|---|
| B768 | 0.004 | 0.003 | 0.009 | 0.240 | 0.217 | 1.000 |
| C_same_classification | 0.000 | 0.000 | 0.001 | 0.917 | 1.000 | 1.000 |
| C_same_search_query | 0.000 | 0.000 | 0.001 | 0.907 | 1.000 | 1.000 |
| C_alt_classification | 0.000 | 0.000 | 0.002 | 0.960 | 0.983 | 1.000 |
| C_alt_search_query | 0.000 | 0.000 | 0.001 | 0.957 | 1.000 | 1.000 |
| C_xlang_classification | 0.000 | 0.000 | 0.001 | 0.873 | 0.983 | 1.000 |
| C_xlang_search_query | 0.000 | 0.000 | 0.002 | 0.873 | 0.933 | 1.000 |
| D2_same_paired | 0.000 | 0.000 | 0.001 | 0.977 | 1.000 | 1.000 |
| D2_same_single | 0.110 | 0.040 | 0.492 | 0.333 | 0.150 | 0.500 |
| D2_alt_paired | 0.004 | 0.001 | 0.015 | 0.980 | 1.000 | 1.000 |
| D2_alt_single | 0.212 | 0.110 | 0.712 | 0.657 | 0.900 | 0.783 |
| D2_xlang_paired | 0.001 | 0.001 | 0.005 | 0.983 | 1.000 | 1.000 |
| D2_xlang_single | 0.131 | 0.100 | 0.330 | 0.550 | 0.767 | 0.717 |

底線為 T1 + T3-word，共 360 筆；T0 僅重編碼一次檢查浮點決定性，見 determinism.json。

## v1 日期前提的核對

v0.2 文件稱「三個語意 arm 全盲」，但 v1 實際分數不支持此概括。以下重算使用各類原始資料；A/B/C 的高分也不能證明有日期推理，因 v1 日期負例改一字、正例改三至四字，編輯幅度未受控。

| v1 arm | T5/T4 AUROC | T4 mean | T5 mean |
|---|---|---|---|
| A | 1.000 | 0.007 | 0.025 |
| B768 | 1.000 | 0.001 | 0.009 |
| C_classification | 0.997 | 0.000 | 0.001 |
| C_search_query | 0.991 | 0.000 | 0.001 |
| D_NLI | 0.485 | 0.993 | 0.990 |

## T9 敏感度分析

| arm | T3 confirmed | T3+T9 assumed negative |
|---|---|---|
| A | 0.972 | 0.986 |
| B768 | 0.930 | 0.920 |
| D1 | 1.000 | 0.850 |
| C_same_classification | 1.000 | 1.000 |
| C_same_search_query | 1.000 | 1.000 |
| C_alt_classification | 1.000 | 0.995 |
| C_alt_search_query | 0.993 | 0.984 |
| C_xlang_classification | 1.000 | 1.000 |
| C_xlang_search_query | 1.000 | 1.000 |
| D2_same_paired | 0.999 | 0.999 |
| D2_same_single | 0.881 | 0.883 |
| D2_alt_paired | 0.985 | 0.961 |
| D2_alt_single | 0.951 | 0.952 |
| D2_xlang_paired | 1.000 | 0.999 |
| D2_xlang_single | 0.922 | 0.928 |
| R | — | — |

## 合併負例對照（次要）

這張表沿用 v1 的 T1+T2+T3+T4 合併負例，不能取代上方主表。

| 配對 | A | B768 | D1 | C_same_classification | C_same_search_query | C_alt_classification | C_alt_search_query | C_xlang_classification | C_xlang_search_query | D2_same_paired | D2_same_single | D2_alt_paired | D2_alt_single | D2_xlang_paired | D2_xlang_single |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T5-word | 0.128 | 0.170 | 0.956 | 0.096 | 0.032 | 0.185 | 0.290 | 0.218 | 0.050 | 0.346 | 0.528 | 0.472 | 0.515 | 0.289 | 0.536 |
| T6-word | 0.527 | 0.583 | 0.978 | 0.956 | 0.949 | 0.963 | 0.929 | 0.961 | 0.944 | 0.974 | 0.837 | 0.979 | 0.921 | 0.970 | 0.867 |
| T6-sentence | 0.875 | 0.891 | 0.965 | 0.999 | 0.999 | 0.998 | 0.993 | 0.998 | 0.996 | 1.000 | 0.987 | 1.000 | 0.989 | 1.000 | 1.000 |
| T7-word | 0.612 | 0.625 | 0.992 | 0.980 | 0.986 | 0.977 | 0.958 | 0.982 | 0.975 | 0.996 | 0.863 | 0.998 | 0.969 | 0.994 | 0.928 |
| T7-sentence | 0.837 | 0.820 | 0.969 | 0.997 | 1.000 | 0.999 | 0.994 | 0.998 | 0.998 | 1.000 | 1.000 | 1.000 | 0.997 | 1.000 | 0.988 |
| T8-sentence | 0.903 | 0.879 | 0.705 | 1.000 | 0.999 | 0.996 | 0.976 | 0.999 | 0.995 | 0.996 | 0.874 | 0.981 | 0.964 | 0.980 | 0.922 |
| T8-paragraph | 0.960 | 0.949 | 0.308 | 1.000 | 1.000 | 1.000 | 0.996 | 1.000 | 0.996 | 1.000 | 1.000 | 0.996 | 1.000 | 1.000 | 1.000 |

## 檔案與未跑項目

- `metrics.json`：完整分層、逐對勝率、分數門檻及 H1–H7 數值。
- `extremes.jsonl`：每個 T0–T10 類別 5 筆極端例句，按 C-same classification 排序取兩端；這是診斷抽查，不是獨立驗證。
- `manifest.json`：模型 revision、環境版本、輸入與評分程式 SHA256；`data/synthetic-v2/analysis-plan.json` 保存評分前的判讀方式。
- 未跑：Gemini 生成與覆核、E、B2、D2-DM。J 屬後續 v0.2.1，分開記錄。

# Handoff v0.2：EG2 狀態偵測 — 「C 是語意還是詞彙」與「標籤投影一步到位」

版本 v0.2 · 2026-10-14 · 承接 `results/synthetic-v1`（v0.1 規格見 `docs/protocol-v0.1.md`）
交接對象：Claude Code 或任何能跑 Python 的 agent。既有程式在 `src/`，沿用其 config、revision 釘死、資料凍結與缺值不填零的規矩。

## 0. 一句話

v0.1 已證明原始 cosine 距離量的是改動量不是意義（B 線收掉）。v0.2 只做四件 v0.1 沒有任何證據的事：
(1) 標籤投影 C 看見的是語意還是詞彙重疊；(2) 把 NLI 的 hypothesis 換成狀態標籤，一次抓翻轉和新增；
(3) 瀰散型改變（沒有任何一句單獨翻轉）抓不抓得到；(4) 值的改變交給規則後，整條管線的分工成不成立。

## 1. 已定案、不再重跑

| 結論 | 證據（synthetic-v1） | 處置 |
|---|---|---|
| B（raw cosine）= 改動量 | T6/T7 word 距離 0.005–0.012 < T1 錯字 0.029 | B768/B256 **只保留為對照欄**，不調維度、前綴、pooling |
| NLI(old,new) 看不見新增 | T8 contradiction 0.03–0.19 | 保留為 D1 對照欄 |
| 值改變三 arm 全盲 | NLI 對 T4=0.993、T5=0.990 分不開；v0.1 的 H5「反例」是合併負例稀釋出來的假象 | 值改變改走規則（R arm） |
| T0 雜訊底線無意義 | p95 = 6.5e-13，是浮點決定性 | T0 只跑 1 次做決定性檢查；雜訊底線改定義（§5） |

## 2. 要回答的問題（寫死）

| # | 問題 | 回答形式 |
|---|---|---|
| Q1 | C 用**英文標籤對中文段落**（及反向）時，T6/T7 word 的 AUROC 掉多少？ | 三組標籤（同語同詞／同語異詞／跨語）× 配對 AUROC 表 |
| Q2 | C 用**同語但不同用語**的標籤（卡關→停滯、落後→延誤、blocked→stalled）時掉多少？ | 同上 |
| Q3 | D2 = NLI(new, 狀態標籤) 能否同時抓翻轉（T6/T7）和新增（T8）？ | 配對 AUROC；與 C、D1 並列 |
| Q4 | 瀰散型改變 T10：每段單獨都不觸發時，文件集層級加總能否觸發？ | 段落層級觸發率 vs 文件集層級 AUROC |
| Q5 | R arm（日期規則）在 T5 vs T4 配對上 AUROC 是否接近 1？與 C 組合後整體如何？ | 配對 AUROC；組合規則寫死（§6） |
| Q6 | 底稿換成 5 個骨架 + LLM 改寫後，v0.1 的 C 高分還在嗎？ | 分骨架、分生成器的 AUROC |
| Q7 | 良性改動的距離分布（新雜訊底線）在 B 與 C 各是多少？狀態翻轉落在底線上方還是下方？ | mean/p50/p95 + 翻轉落點比例 |

## 3. 資料

### 3.1 底稿多樣化（修 v0.1 單一模板問題）

- **5 個不同骨架**，不得共用固定尾句：進度週報段、ADR 狀態段、工單描述、會議記錄要點、PRD 里程碑段。每骨架中英各 ≥ 20 段（含 slot 填入），總底稿 ≥ 200 段。
- 另用 Gemini **3.6-flash**（3.5 已停用自動轉 3.6，config 的 `requested_model_status` 已記）把其中一半底稿**改寫成不同語體**（口語、條列、正式），`thinkingLevel: "minimal"`，每筆落盤再呼叫下一筆，沿用 `results/api-ledger.jsonl` 與 US$1 保險絲。改寫後的段落經 `check_llm` 確認狀態未變才收。
- 每個 T6 子類（五種中文否定、五種對應英文）≥ **30 個不同底稿**，不再用 5 底稿 × 3 強度充數。強度分級保留，但 AUROC 主表以 word 層級為主（這是 v0.1 顯示最難的層級）。

### 3.2 擾動類別

沿用 T0–T9 定義，變更如下：

| 代號 | 變更 |
|---|---|
| T0 | 只跑 1 次，100 筆，做決定性檢查 |
| T1 | 補足錯字子類（v0.1 只做格式），中文錯字用同音／形近替換 |
| T3 | 加 LLM 改述半邊（3.6-flash），與規則半邊各半，分開列 |
| T5/T4 | 兩者對同一底稿成對生成，日期編輯字元數相同（只差跨不跨截止日） |
| T6/T7 | 詞彙**不得與任何一組標籤描述共用**狀態詞（見 §4 三組標籤），由程式檢查 |
| **T10 瀰散型（新）** | 一份「文件集」= 同一專案 3 段（來自不同骨架）。正例：三段各做一個單獨不構成狀態改變的小改動（日期後移但未超期、加一句「等客戶確認」、負責人換人），加總後人工判定為「狀態已變」；負例：三段各做 T1/T3 良性改動。≥ 40 組文件集，中英各半。ground truth 由兩個獨立 prompt 判讀一致才收，不一致者計數並排除 |

### 3.3 配對對照（修 v0.1 合併負例問題）

每個正例類別指定**專屬負例**，不再合併：

| 正例 | 負例 | 配對原則 |
|---|---|---|
| T5 | T4（同底稿） | 同樣改日期，只差跨不跨截止日 |
| T6 word / T7 word | T3 word（同底稿） | 同樣改一個詞 |
| T6 sentence / T7 sentence | T3 sentence | 同樣改一句 |
| T8 sentence | T3 sentence + T9 | 同樣多／少一句 |
| T8 paragraph | T3 paragraph | 同樣大改 |
| T10 正例 | T10 負例 | 同樣三段各改一點 |

v0.1 的合併負例表**另出一份**當對照，不做主表。

## 4. 方法 arm

### 4.1 保留（對照欄）

A、B768、D1 = NLI(old, new) 雙向取 contradiction 最大值。不調整。

### 4.2 C 的三組標籤（回答 Q1、Q2）

| 組 | 標籤語言 | 用語 | 目的 |
|---|---|---|---|
| C-same | 與段落同語 | **刻意與擾動詞重疊**（阻礙／落後／取消／blocked／behind） | 重現 v0.1，當上限 |
| C-alt | 與段落同語 | **刻意不重疊**（停滯／延誤／終止／stalled／slipping／dropped），由程式檢查與 T6/T7 擾動詞零重疊 | 去詞彙 |
| C-xlang | 與段落**異語**（中文段落配英文標籤、英文段落配中文標籤） | 任意 | 去詞彙的最強版本 |

標籤仍為四類（on track／延後／卡關／取消），每類 1–2 句描述。前綴沿用 v0.1：段落 `Document`，標籤 `Classification` 與 `SearchQuery` 各跑一次。分數定義不變：`1 − cos(p_old, p_new)`，溫度 0.045（仍標註無官方背書）。

**判讀規則（寫死）**：C-xlang 在 T6/T7 word 配對 AUROC ≥ C-same − 0.10 → C 量的是語意；≤ 0.60 → C 的 v0.1 成績是詞彙重疊，C 線降級為「只在文件用語與標籤一致時可用」。

### 4.3 D2 = NLI(new, 狀態標籤)（回答 Q3，新）

- 對 new 段落，對四個標籤各算 `entailment − contradiction`，得四維分數向量；對 old 同樣算。
- 主分數：`1 − cos(s_old, s_new)`；副分數：argmax 是否改變；再加一個**單邊分數** `max_label(entail(new, 卡關 ∪ 延後 ∪ 取消))`，不需要 old，用來看「不配對能不能做」。
- 標籤三組（same／alt／xlang）同 C。
- 模型沿用 `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` 釘死 revision；若 Decision Maker Laya/GLiNER 在 Linux 裝得起來就**另開一欄 D2-DM**，裝不起來寫「未跑」。

**判讀規則**：D2 在 T8 配對 ≥ 0.85 且 T6/T7 word ≥ 0.85 → 「標籤投影一步到位」成立，架構不需要 old-new 配對；T8 < 0.70 → 新增仍需另一條路（§6 組合）。

### 4.4 R = 規則（回答 Q5，新）

- 從 old/new 各抽「預計交付日」與「截止日」（regex，中英日期格式各寫一組），`score = 1 if new.planned > new.deadline and old.planned ≤ old.deadline else 0`；抽不到日期給 `None`，不填 0。
- 只在 T5 vs T4 配對上評；其他類別 R 不適用，表格填「不適用」。

### 4.5 T10 的文件集層級分數

- 段落層級：對三段各算 C／D2 分數，記「任一段超過該 arm 在 T3 配對上的 p95」的觸發率。
- 文件集層級：三段分數取 max、mean、以及 D2 單邊分數對三段的 max，各出一個 AUROC。
- 判讀：段落觸發率 < 30% 而文件集 AUROC ≥ 0.80 → 加總有效；兩者都低 → 瀰散型是目前所有語意方法的盲區，記錄不解釋。

## 5. 新雜訊底線（回答 Q7）

- 底線 = **T1 + T3-word 的距離分布**（良性改動），對 B、C-same、C-alt、C-xlang、D2 各算 mean/p50/p95。
- 對每個正例類別，報「分數落在底線 p95 之上的比例」。v0.1 已知 B 的翻轉全在底線之下；v0.2 看 C／D2 是否翻到上方。

## 6. 組合規則（寫死，不調）

`score_final = max(R, D2_single)`；R 抽不到日期時 `score_final = D2_single`。
只在三個配對上評：T5/T4、T6-word/T3-word、T8-sentence/T3-sentence。目的是驗證「值交規則、類別交投影」的分工，不是找最佳組合；任何其他組合方式寫進報告都算違規。

## 7. 假說與 kill criteria

| # | 假說 | 成立 | 不成立 |
|---|---|---|---|
| H1 | C-xlang ≥ C-same − 0.10（T6/T7 word 配對） | C 是語意，Phase 2 上真文件 | C 是詞彙，C 線降級；Phase 2 改以 D2 為主 |
| H2 | C-alt 介於 C-xlang 與 C-same 之間 | 符合預期 | 若 C-alt < C-xlang，記錄現象不解釋 |
| H3 | D2 在 T8 配對 ≥ 0.85 | 新增問題解決，不需要 old-new | D2 也看不見新增，T8 另找路（可能回到 A 的長度訊號） |
| H4 | D2 單邊分數（不用 old）在 T6/T7/T8 ≥ 0.80 | 不配對也能做，架構大幅簡化 | 配對仍是必要的 |
| H5 | R 在 T5/T4 ≥ 0.95 | 值走規則定案 | regex 覆蓋不足，列出抽取失敗樣本 |
| H6 | T10 文件集層級 ≥ 0.80 且段落觸發率 < 30% | 加總有效 | 瀰散型為盲區，Phase 2 真文件要專門量這類佔比 |
| H7 | 分骨架的 C 成績差 < 0.10、LLM 改寫 vs 規則差 < 0.10 | v0.1 結論不是單一模板產物 | 結果受模板主導，Phase 1 結論全部降級為「模板內成立」 |

平手規則維持 < 0.05。

## 8. 執行順序

1. 寫五骨架模板 + slot 生成器 → `data/synthetic-v2/base.jsonl`（含 `skeleton` 欄）
2. Gemini 3.6-flash 改寫一半底稿 + check_llm 確認；記丟棄率（先驗證模型 ID 與 3.6 價格再呼叫）
3. 規則／LLM 擾動生成，T10 文件集另存 `data/synthetic-v2/docsets.jsonl`；三組標籤存 `config.json` 的 `labels_same / labels_alt / labels_xlang`，程式檢查 alt 與擾動詞零重疊
4. **凍結資料**（sha256 進 manifest），再開始評分
5. 跑 A/B768/D1 對照欄 → C 三組 × 兩前綴 → D2 三組 → R → T10 文件集
6. 新雜訊底線、配對 AUROC 主表、合併負例對照表
7. `results/synthetic-v2/report.md` + `summary.md`：Q1–Q7 逐條、H1–H7 逐條、每類 5 筆極端樣本

## 9. 不做

- 不調 B 的任何設定；不為 H1 失敗找補救。
- 不跑 E（LLM 天花板）、不跑 B2。
- 不在看過 T7 或 T10 分數後改標籤文字或擾動詞表；要改就開 synthetic-v3。
- 不宣稱真實專案的準確率；所有結論前綴「在合成骨架內」。

## 10. 交付物

- `data/synthetic-v2/{base,pairs,docsets}.jsonl`、`manifest.json`、`analysis-plan.json`
- `config.json` 新增三組標籤與 R 的日期 regex
- `src/arms.py` 新增 `score_c(labels_set)`、`score_d2(labels_set)`、`score_r`、`score_docset`
- `results/synthetic-v2/{scores,docset-scores}.jsonl`、`report.md`、`summary.md`、`fig/`
- README 更新：v0.1 結論三條（§1）、v0.2 新增 arm 與判讀規則、Gemini 版本變更紀錄

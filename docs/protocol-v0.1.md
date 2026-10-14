# Handoff：EG2 能不能偵測「專案狀態變了」— 合成資料階段（Phase 1）

版本 v0.1 · 2026-10-14 · 交接對象：Claude Code（或任何能跑 Python 的 agent）

## 0. 一句話

用受控的合成擾動，量 EmbeddingGemma 2（EG2）在「兩版文件之間，狀態有沒有變」這題上**哪些擾動看得見、哪些看不見**，並決定 vector diff / 標籤移動 / cross-encoder 三種做法哪個留下。這一階段**只回答「做不到」與「方法排序」**，不調門檻、不算精確率，那些留給真實資料階段。

## 1. 要回答的問題（寫死，跑完逐條回）

| # | 問題 | 回答形式 |
|---|---|---|
| Q1 | 段落配對後的 cosine 距離，能不能把「錯字／改述」和「新增阻礙段落」分開？ | 分類別 AUROC |
| Q2 | 否定翻轉、反義替換（狀態真的變了，但字面改很少）時，cosine 動不動？ | 該類別 AUROC + 距離分布圖 |
| Q3 | 「對狀態標籤的 argmax 移動」（C）比純距離（B）強多少？ | 兩者分類別 AUROC 差 |
| Q4 | cross-encoder 三向驗證（D）在否定／反義類能不能補 B 的洞？ | D 在該兩類的 AUROC |
| Q5 | 中文否定形態（沒有／不再／尚未／取消／暫停）哪些 EG2 完全看不見？ | 每形態一列的表 |
| Q6 | 同一段落、同設定重跑，cosine 的自然抖動多大？ | 雜訊底線（mean/std/p95） |
| Q7 | 擾動強度（1 詞 / 1 句 / 1 段）對距離的靈敏度曲線 | 一張圖 + 表 |
| Q8 | 在沒拿來調任何東西的 holdout 類別上，方法排序是否維持？ | holdout AUROC 表 |

## 2. 範圍

**做**：純文字（中文 + 英文各半）、段落層級、單點擾動、五個方法 arm、固定報表。

**不做**（Phase 2 以後）：真實 git history、門檻調整、精確率、多文件瀰散型改變、多模態、EG2 fine-tune。

## 3. 環境

- 跑在 Azure 開發 VM 或 Crostini 都可，**CPU 即可**；EG2 text-only 270M 約 165 MB，8 GB RAM 綽綽有餘。
- Python 3.11+。
- 相依：`sentence-transformers`（載 `google/embeddinggemma-2`，`vision_config=None, audio_config=None` 只載文字塔）、`numpy`、`scikit-learn`（roc_auc_score）、`matplotlib`。
- **精度**：EG2 activations 與 float16 不相容，一律 `torch_dtype=bfloat16` 或 float32。
- D arm 用 `pip install mediapipe` 的 Decision Maker Python API，model path 用 Laya（`laya_s512.task`）或 GLiNER2.5-Decide（`gliner_s512.task`）；兩者都跑就兩者都記，不要只跑一個然後外推。
- 若 mediapipe 的 Decision Maker 在 Linux 裝不起來或 cross-encoder 模型檔抓不到：**換任一 NLI cross-encoder**（例如 `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`，要支援中文），並在報告裡明寫「D arm 用的是 NLI 替代，不是 Decision Maker」。
- 文字前綴：EG2 文字輸入要帶 task prefix；B arm 兩邊都用 `Document` 前綴（對稱比較）；C arm 段落用 `Document`、標籤描述用 `Classification`／`SearchQuery`（兩種都試，記下哪種較好，不要只試一種）。
- 模型 ID、前綴字串、Decision Maker 模型檔名**先查官方頁面驗證再寫進 config**，不要憑記憶。

## 4. 資料

### 4.1 底稿（真文件，不是 LLM 編的）

- 從 Clarence 的 repo 取 **20 份** markdown（ADR、報告、PRD 皆可，中英各約 10 份）。
- 每份取 5–10 段「描述專案狀態或進度」的段落（有時程、負責人、阻礙、完成度這類內容的段落優先），每段 80–400 字。
- 這些是 **base 段落**，總數目標 150–200 段。每段記 `{doc_id, para_id, lang, text}`。

### 4.2 擾動類別（每個 base 段落每類各生 1 筆，不夠就 2 筆）

| 代號 | 擾動 | 狀態變了？（ground truth） | 生成方式 |
|---|---|---|---|
| T0 | 完全相同（雜訊底線用） | 否 | 複製 |
| T1 | 錯字 2–3 處、標點／格式改動 | 否 | 規則 |
| T2 | 段落內句子重排（句序打亂，內容不變） | 否 | 規則 |
| T3 | 同義改述（保留所有事實與狀態） | 否 | LLM |
| T4 | 日期改、狀態不變（5/10 → 5/25，仍在時程內） | 否 | 規則 + LLM 確認 |
| T5 | 日期改、狀態變（5/10 → 9/30，明顯超期或延後） | **是** | 規則 + LLM 確認 |
| T6 | 否定翻轉（尚未→已、不再卡關→卡關、已完成→未完成） | **是** | 規則（模板）+ LLM 各一半 |
| T7 | 反義替換（ahead→behind、順利→受阻、on track→delayed） | **是** | 規則 + LLM 各一半 — **holdout，不拿來調任何設定** |
| T8 | 新增一句或一段阻礙／延期描述 | **是** | LLM |
| T9 | 刪掉一句關鍵狀態句（其餘不變） | 標記為 `ambiguous`，報表單獨列，不進 AUROC | 規則 |

中文否定另外拆子類：`T6-zh-沒有`、`T6-zh-不再`、`T6-zh-尚未`、`T6-zh-取消`、`T6-zh-暫停`，每子類至少 15 筆。

### 4.3 擾動強度分級（給 Q7）

對 T3、T6、T8 各做三級：改 1 個詞 / 改 1 句 / 改整段。記 `strength ∈ {word, sentence, paragraph}`。

### 4.4 生成規則

- **兩個生成器**：規則模板一套、LLM 一套。LLM 生成的用 Gemini 3.5-flash，`thinkingLevel: "minimal"`（照 gemini-api-lessons），每筆都存檔再呼叫下一筆，設 token 上限保險絲；總量幾百筆，預算幾十塊台幣以內。
- 規則生成與 LLM 生成的筆數在同一類裡各半，報表要**分開列**（看生成器指紋）。
- 每筆 LLM 生成結果要過一道**獨立檢查**：另一個 prompt 判「狀態有沒有變」，跟預設 ground truth 不一致的丟掉並計數（丟棄率寫進報告）。
- 資料格式：`data/pairs.jsonl`，每行 `{pair_id, base_id, lang, category, subcategory, strength, generator, old_text, new_text, label, ambiguous}`。

### 4.5 數量目標

每類（不含 T0、T9）≥ 60 筆，中英各半；T0 ≥ 100 筆；總量約 700–900 筆。

## 5. 方法 arm（各自一個函式，輸入 pair，輸出一個分數，分數愈高＝愈可能「狀態變了」）

| Arm | 定義 | 備註 |
|---|---|---|
| **A** diff baseline | `difflib` 字元級編輯距離 / 舊段落長度 | 不用模型，代表「改得多就是變了」 |
| **B** vector diff | `1 − cos(EG2(old), EG2(new))`，768 維 | 另外記 256 維結果（MRL 截斷）看掉多少 |
| **B2** token-level alignability | 對 new 的每個 token embedding，取它對 old 所有 token 的最大 cos，`score = 1 − mean(max_cos)`；需要 `output_value="token_embeddings"` | Vamvas 式；若 sentence-transformers 拿 token embeddings 麻煩就跳過，報告寫明「未跑」 |
| **C** 標籤移動 | 四個狀態描述（on track／延後／卡關／取消，各寫 1–2 句帶具體關鍵字的描述，中英各一套），對 old、new 各算 cos；`score = 1 − cos(p_old, p_new)`（兩版對標籤的機率分布距離），同時記 `argmax 是否改變` | 溫度先用 Google 文件的 0.045 做 softmax；另記 raw cosine 的 argmax |
| **D** cross-encoder 三向 | premise=old、hypothesis=new（反向也跑一次），取 `contradiction` 機率 | 雙向取 max |
| **E** LLM 判讀（天花板） | Gemini 3.5-flash，`thinkingLevel: "minimal"`，問「狀態有沒有變，變了什麼」，輸出 0/1 + 一句理由 | 只跑一次做 sanity，別用來調 B/C/D |

**重複量測（Q6）**：B arm 對 T0 全部 100 筆跑 3 次（換 batch size、換段落順序），記 cosine 的 mean/std/p95。這是雜訊底線，任何「差異」小於 p95 一律視為沒差異。

## 6. 指標與報表（格式固定，填表即可）

### 6.1 主表：分類別 AUROC（label = 狀態變了）

對每個類別 Tk（k≥1），負例固定用 T1+T2+T3+T4 全體，正例用該類別，各 arm 算 AUROC。

| 類別 | n | A | B(768) | B(256) | B2 | C | D | E |
|---|---|---|---|---|---|---|---|---|
| T5 日期改、狀態變 | | | | | | | | |
| T6 否定翻轉（全） | | | | | | | | |
| T6-zh 各子類（5 列） | | | | | | | | |
| T6-en | | | | | | | | |
| T7 反義（holdout） | | | | | | | | |
| T8 新增阻礙 | | | | | | | | |

同一張表**再分 generator**（rule / LLM）各出一版。

### 6.2 靈敏度表（Q7）

| 類別 | strength | n | B 距離 mean | B 距離 p50 | 超過雜訊 p95 的比例 |
|---|---|---|---|---|---|

### 6.3 雜訊底線（Q6）

T0 的 B 距離：mean / std / p95 / max，三次重跑各一列。

### 6.4 分布圖

每個類別一張 B 距離直方圖，疊在 T0 分布上；T6、T7 額外疊 D 的 contradiction 機率。

### 6.5 失敗樣本

每個類別各列 5 筆「分數最離譜」的 pair（正例分數最低、負例分數最高），附原文，供人工看。

## 7. 假說與 kill criteria（事先寫死，跑完對照，不改）

| # | 假說 | 若成立 | 若不成立 |
|---|---|---|---|
| H1 | B 在 T8（新增阻礙）vs 負例 AUROC > 0.85，且明顯高於 A | B 至少能當「有意義改動」的篩子 | **整條 vector diff 線砍掉**，EG2 在這題只剩 D 或 LLM |
| H2 | B 在 T6、T7 的 AUROC < 0.65 | 確認 bi-encoder 看不見否定／反義，B 定位＝篩子，不是偵測器 | B 比預期強，需要追查是不是生成器指紋（看 rule vs LLM 分開的表） |
| H3 | C 在 T6、T7 介於 B 與 D 之間 | C 值得留，便宜 | 若 C ≈ B，C 沒有額外價值，砍 |
| H4 | D 在 T6、T7 的 AUROC > 0.80 | 狀態翻轉交給 cross-encoder，架構定案為 B 篩 + D 判 | **< 0.70**：Decision Maker 現成 cross-encoder 不夠，Phase 2 要換 NLI 專用模型或上 Gemma 4 後端 |
| H5 | T5（日期改、狀態變）所有 arm 都 < 0.70 | 確認「值改變」是所有語意方法的盲區，這類要靠規則（日期抽取 + 比較） | 若某 arm 意外能做，記錄現象，**不補解釋**（v9 L/M 紀律） |
| H6 | rule 與 LLM 生成的同類別 AUROC 差 < 0.10 | 生成器指紋可忽略 | 差 > 0.10：結果不可信，先解決生成器問題再談方法 |
| H7 | holdout T7 上的 arm 排序與 T6 一致 | 排序可外推 | 排序翻轉：Phase 1 結論只限於看過的擾動類型 |

**雜訊規則**：任何兩個 arm 之間 AUROC 差 < 0.05 視為打平，不排序。

## 8. 執行順序

1. 收底稿 → `data/base.jsonl`（半天）
2. 規則生成器 → T0/T1/T2/T4/T5/T6/T7/T9 的 rule 半邊（半天）
3. LLM 生成器 + 獨立檢查 → T3/T5/T6/T7/T8 的 LLM 半邊，記丟棄率（半天，含保險絲）
4. **先跑 Q6 雜訊底線**，再跑 A/B/B2/C（半天）
5. 跑 D（兩個 cross-encoder 或 NLI 替代）（半天）
6. 跑 E，只抽 200 筆（控制花費）
7. 出報表 `results/report.md` + 圖 `results/fig/`，逐條回 Q1–Q8，逐條對 H1–H7

## 9. 已知坑（照這份 repo 的既有規矩）

- 「我們沒測」「我們沒開」「它沒有」是三件事。任何一格沒跑就寫「未跑」，不准填估計值。
- 缺格不能當保守估計交差：T5 預判全弱，**仍然要跑**。
- 假說被推翻後不要立刻猜第二個解釋，先把現象記下來。
- A/B 兩條控制：先量同設定自然變異（Q6）再談差異；一致 ≠ 正確，每類抽 5 筆人工看（6.5）。
- 批次與即時是不同的東西：這裡全是批次，結論不外推到串流情境。
- LLM 生成和 LLM 判讀（E）可能是同一家模型，E 的分數偏高是預期中的，不當真實天花板，只當 sanity。
- 中文要用台灣用語生成擾動，不要出現簡體或大陸詞（會讓距離量到的是語體差異而不是狀態差異）。

## 10. 交付物

- `data/base.jsonl`、`data/pairs.jsonl`
- `src/arms.py`（五個 arm 各一函式，統一簽名 `score(old_text, new_text) -> float`）
- `src/gen_rule.py`、`src/gen_llm.py`、`src/check_llm.py`
- `results/scores.jsonl`（每 pair 每 arm 一個分數）
- `results/report.md`（第 6 節格式 + 第 1 節 Q1–Q8 逐條回答 + 第 7 節 H1–H7 逐條對照）
- `results/fig/`
- `README.md`：怎麼重跑、用了哪個模型 ID 與版本、Decision Maker 或 NLI 替代用了哪個

Phase 2（真實 git history、門檻、精確率）另開 handoff，等這份報告出來再寫。

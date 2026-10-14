# EG2 狀態漂移實驗：本次執行結果

**尚未完成 Phase 1，不能判斷 EG2 能否偵測狀態改變，也不能淘汰或排序 B／C／D。**

本次完成官方規格查核、實驗程式、CPU 相依安裝、14 項測試及 20 筆人工例句的 A baseline 診斷。
正式資料是 0 筆；EG2／NLI 權重下載受 proxy 403 阻擋；沒有 Gemini API 呼叫或費用。

## 已實際驗證

| 項目 | 結果 |
|---|---|
| 原始 repo | `clarencechien/eg2poc`，commit `1f46480242ec652084b71f79a1d785b2856c3feb`；當時只有 README 標題 |
| 真實底稿抽取 | 0 段，無法產生合規的 700–900 筆資料集 |
| 程式測試 | 14/14 通過：AUROC 固定負例、缺值、T9 排除、生成器分組、cosine、預算停止等 |
| CPU 相依 | PyTorch 2.14.1+cpu、Transformers 5.19.0、SentenceTransformers 6.1.0 已安裝；pip check 通過 |
| A baseline | 人工中英例句各 10 筆，共 20 筆，評分與報表已跑通 |
| B／C | 下載 EG2 權重失敗，未產生模型分數 |
| D | 官方 NLI 模型／label mapping 已核對；其權重同樣轉址至被擋 CDN，未推論。不是 Decision Maker |
| B2 | optional arm，未實作、未跑 |
| E／LLM 生成及覆核 | 無憑證，未呼叫；API 客戶端仍待實際驗證 |

診斷詳細輸出：[diagnostic-a/report.md](diagnostic-a/report.md)。
模型下載失敗紀錄：[diagnostic-models/manifest.json](diagnostic-models/manifest.json)。
`data/base.jsonl`、`data/pairs.jsonl` 與正式 `results/scores.jsonl` 留空；不填入假資料冒充正式結果。

## 診斷數字（只驗證管線，無實驗推論效力）

每列僅 2 個人工正例，以相同的 8 個人工負例 T1–T4 計算。例句不是來自真文件，未經 Gemini 獨立覆核。

| 類別 | A AUROC | B768 | B256 | B2 | C | D | E |
|---|---:|---|---|---|---|---|---|
| T5 日期／延後 | 0.5000 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 |
| T6 否定 | 0.3125 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 |
| T7 反義 | 0.4375 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 |
| T8 阻礙 | 0.5000 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 | 未跑 |

這些數字只證明程式可以產生非平凡 AUROC，**不能作為 A 的可靠表現估計，更不是 EG2 的結果**。
人工例句與正式資料隔離，T7 診斷例句不能替代正式 holdout。

## 官方規格查核

- [EG2 官方 model card](https://huggingface.co/google/embeddinggemma-2)：名稱存在，無 gated 授權要求；
  text-only 270M，完整模型 740M，輸出 768 維；float32／bfloat16，不能 float16。
  固定 revision `914f7f89142e33e77833254d9c9b90c3cef7303b`。
- Document、Classification、SearchQuery 的實際字串已按 model card 寫入 `config.json`。
  256 維 cosine 會重新正規化。0.045 是交接指定值，已讀 model card 未找到官方背書。
- [NLI 官方 model card](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)：
  固定 revision `b5113eb38ab63efdd7f280f8c144ea8b13f978ce`，contradiction label index 2；程式從 config 驗證而非硬猜。
- [Gemini 3.5 Flash 官方頁](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash) 明載：
  **3.5 已停用，API 請求自動轉到 3.6**。因此即使繼續使用舊 ID，也不能宣稱測到 3.5。
  此次沒有擅自把另一個 Gemini 版本記為原指定版本。
- Decision Maker 官方文件路徑查詢仍遇到 proxy 403；不能由此斷言該 API 或模型不存在。

## Q1–Q8

| 問題 | 本次答案 |
|---|---|
| Q1 cosine 能分開錯字／改述和新增阻礙？ | 未跑 B，無法回答 |
| Q2 否定／反義是否看得見？ | 未跑 B，沒有距離分布；不能用 A 推論 |
| Q3 C 比 B 強多少？ | 未跑兩者，無法計算 AUROC 差 |
| Q4 D 能補 B 的洞？ | NLI 推論未跑；也沒有 Decision Maker 結果 |
| Q5 哪種中文否定完全看不見？ | 五類都沒有合格樣本或 EG2 分數，無法判定 |
| Q6 自然抖動多大？ | 未跑，mean/std/p95/max 均不可填零；三次 batch/order 量測程式已備妥 |
| Q7 擾動強度曲線？ | 未跑 B，不產生看似實測的曲線 |
| Q8 holdout 排序維持？ | 沒有正式 T7 或多 arm 分數，無法比較；人工 fixture 不算 holdout 證據 |

## H1–H7

| 假說 | 判定 | 缺少的必要證據 |
|---|---|---|
| H1 B 在 T8 >0.85 且優於 A | 無法判定 | 真實底稿擾動與 B 分數 |
| H2 B 在 T6／T7 <0.65 | 無法判定 | B 分數 |
| H3 C 介於 B 與 D | 無法判定 | B、兩種 C prefix、D |
| H4 D 在 T6／T7 >0.80 | 無法判定 | D 分數；若用 NLI，結論只能限於該替代模型 |
| H5 T5 所有 arm <0.70 | 無法判定 | A 的微型人工診斷不足，其他 arm 未跑 |
| H6 rule 與 LLM 差 <0.10 | 無法判定 | 合格 rule／LLM 平衡資料與獨立檢查拒絕率 |
| H7 holdout 方法排序一致 | 無法判定 | 完整 T6／T7 多 arm 分數 |

## 規格中需保留的限制

- 正式 6.1 表應只以 T5–T8 作正例；T1–T4 自身都是負例，不可照「每個 Tk 都當正例」字面計算。
- 第 4.4 節「每類生成器各半」與 T1/T2/T9 規則、T3/T8 LLM 的指定互相衝突。
  目前保留分生成器表、強制 T5/T6/T7 平衡，不捏造不存在的另一半。正式生成前仍需固定最終計畫。
- T1 目前規則只做格式擾動；要符合錯字子類仍需補資料。語意翻轉候選使用明確替換註記，不對任意段落亂套標籤。
- E 限 200 筆，其分母與全量其他 arm 不同；不能直接比較 AUROC 排序。需用共同子集另算。
- 「明顯高於」沒有顯著性定義；只依既定 <0.05 打平規則，不能擅自宣稱統計顯著。
- 報表程式保留缺值及覆蓋缺口，不會因程式跑完就自動宣告假說成立。

## 繼續執行需要

1. 提供可使用的真實文件 repo／路徑：目標約 20 份、中英各半、150–200 段。
2. 在環境設定套用已儲存的 `us.aws.cdn.hf.co` 網路需求；實際下載測到的是該 hostname，不開放萬用網域。
   `huggingface.co`、`ai.google.dev` 的模型／文件部分請求已成功；這不代表 CDN 已通。
3. 安全設定 `GEMINI_API_KEY`，確認用官方替代版（例如 3.6）後記錄版本差異與定價，再生成及覆核。

可重跑指令、資料註記與預算保險絲見 [README](../README.md)。設定草稿的儲存不代表發布完成。

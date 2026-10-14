# EG2 project status drift — synthetic experiments

目前狀態：**v0.2 與 v0.2.1 J E2B 已完成；J E4B 正在執行。**
最新結果見 [v0.2 摘要](results/synthetic-v2/summary.md)、[完整報告](results/synthetic-v2/report.md)；
J E2B 已完成 single／paired 各 1,230 筆及 T10 共 80 個文件集，全部通過輸出檢核且無缺值，見 [v0.2.1 報告](results/synthetic-v2.1/report.md)。
770 組 v0.1 歷史結果見 [原合成試驗](results/synthetic-v1/summary.md)。
原始真實文件＋雙生成器 Phase 1 尚未完成。原始交接規格保存在
[docs/protocol-v0.1.md](docs/protocol-v0.1.md)。不要將 `tests/fixtures` 人工例句當成真實文件底稿。

## 已確認的模型

| 用途 | 模型 | 固定 revision | 狀態 |
|---|---|---|---|
| B/C | `google/embeddinggemma-2` | `914f7f89142e33e77833254d9c9b90c3cef7303b` | v0.2 的 1,690 組完成，文字塔 271,002,624 參數、float32 |
| D1/D2 | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | `b5113eb38ab63efdd7f280f8c144ea8b13f978ce` | v0.2 的 1,690 組完成；**NLI 替代，不是 Decision Maker** |
| 生成／覆核／E | 原規格 `gemini-3.5-flash` | 不適用 | 官方公告已停用並自動轉到 3.6；尚未選擇替代、沒有 API 呼叫 |

EG2：CPU float32；`config_kwargs={"vision_config": null, "audio_config": null}`。
Document：`title: none | text: {text}`；Classification：`task: classification | query: {text}`；
SearchQuery：`task: search result | query: {text}`。768 維與前 256 維各自做 cosine 正規化。
溫度 0.045 沿用交接規格，**尚未在已讀官方 model card 找到此數值的背書**。
C 保留兩種 prefix 結果，不用 holdout T7 選設定；段落 Document／標籤其他 prefix 是本實驗定義，
不同於官方一般 classification 的對稱前綴建議。

## 環境與驗證

Python 3.12，CPU 最多 4 threads。PyTorch 2.14.1+cpu、Transformers 5.19.0、
SentenceTransformers 6.1.0；所有安裝版本見 `requirements.lock`。
即使只載文字塔，這版 EG2 processor 仍需要 torchvision；已安裝相符的 0.29.1+cpu。

```bash
cd /workspace/eg2poc
bash scripts/install.sh
source scripts/env.sh
.venv/bin/python -m unittest discover -s tests -v
```

此雲端任務已隔離，使用現有 checkout；除非使用者要求，不建立 Git worktree。
不需要常駐服務。TLS、套件驗證保持啟用；不以其他模型假冒 EG2。

## 重跑已驗證的診斷

每次使用新的輸出目錄，避免混入前次結果。以下只有 **20 筆人工測試例句**，不能支持假說。

```bash
source scripts/env.sh
.venv/bin/python -m tests.make_fixture
.venv/bin/python -m src.run --base tests/fixtures/base.jsonl --pairs tests/fixtures/pairs.jsonl \
  --arms A --diagnostic --output results/diagnostic-a-new
.venv/bin/python -m src.report results/diagnostic-a-new
```

模型診斷指令（已於 `results/model-smoke-v3` 跑通）：

```bash
.venv/bin/python -m src.run --base tests/fixtures/base.jsonl --pairs tests/fixtures/pairs.jsonl \
  --arms A B C D --diagnostic --output results/diagnostic-models-new
.venv/bin/python -m src.report results/diagnostic-models-new
```

模型流程已通過實際推論驗證；報表不得將缺分數填為 0。
`results/diagnostic-models/manifest.json` 保存首次下載失敗狀態，只完成 A。
B2 為規格允許跳過的 optional arm，未實作、未跑。E 抽樣上限 200，分層後固定 seed；
其 AUROC 使用抽樣負例，不能直接與其他 arm 全量 AUROC 排序，需另做共同子集比較。

## 重跑 770 組合成資料試驗

```bash
cd /workspace/eg2poc
bash scripts/run-synthetic.sh results/synthetic-v1-repeat
```

使用全新的輸出目錄。這會檢查固定資料的雜湊、跑 A/B/C/D、產生完整報表與 summary。
此次在 4 CPU threads、float32 下花費約 12.4 分鐘（不含首次下載）。
資料：`data/synthetic-v1/base.jsonl`、`pairs.jsonl`、`manifest.json`、`analysis-plan.json`。
建了 180 段底稿，其中 167 段用於 770 組比較；中英各 385 組。
770 組皆有 A/B768/B256/C_classification/C_search_query/D_NLI 六個有效分數。
數值及圖：`results/synthetic-v1/scores.jsonl`、`summary.md`、`summary.json`、`report.md`、`fig/`。
全部是規則模板，不是 Gemini 生成；沒有獨立 LLM 覆核，也沒有 E 判讀。
不能用本結果宣稱真實專案的準確率。C 衡量的是**標籤機率分布距離**，不是只看 argmax 改變。
資料在評分前凍結；不要看過 T7 分數後修改同一版資料。新增資料需建立新版。
T9 有 12 筆只刪中性安排句，未符合刪關鍵狀態句規格；所有 T9 皆排除 AUROC。

## 正式資料與生成

1. 提供可存取的真實 Markdown repositories。抽取的是固定 Git commit 的檔案，不包含未提交文件。
   `python -m src.extract /workspace/your-repo --output data/base-candidates.jsonl`。
   人工檢查語言、狀態內容、80–400 字、20 份文件／150–200 段、中英各半後，
   設 `reviewed: true` 並存成 `data/base.jsonl`。目前該檔為空，因原 repo 沒有合格底稿。
2. `python -m src.gen_rule --base data/base.jsonl --edits data/edits.jsonl`。
   T0/T1/T2 自動建立候選；其他類別用明確的單次替換註記。不能只把任意日期改遠就標為延期。
   T1 目前只實作格式變更，尚未涵蓋錯字子類；正式資料須補足。
3. 事先固定 LLM 生成計畫 `data/llm-plan.jsonl`，不可看 T7 分數後修改。
   補齊 Gemini 設定與官方價格後，`python -m src.gen_llm --plan data/llm-plan.jsonl`。
4. `python -m src.check_llm data/rule-candidates.jsonl data/llm-candidates.jsonl`。
   使用另一個不含預期類別／答案的 prompt 檢查，接受者寫到 `data/pairs.jsonl`；
   所有判斷寫 `data/checks.jsonl`。正式報告需按類別／生成器計算拒絕率並人工抽查。
5. `python -m src.run --arms A B C D --output results/phase1-001`，再執行報表。
   先量 Q6 再算 B/C；輸出含輸入 SHA256、固定 config、套件版本。報告數量缺口會阻止假說結論。
   E 需另指定 `--arms E`，輸出獨立目錄，僅作 sanity。

替換註記範例（只能用與底稿相符且有語意根據的替換）：

```json
{"base_id":"repo/doc.md:3","category":"T6","strength":"word","subcategory":"T6-zh-尚未","before":"尚未完成","after":"已經完成","review_note":"同一交付項目的完成狀態翻轉"}
```

LLM 計畫每行：`{"base_id":"...","category":"T6","strength":"word","subcategory":"T6-zh-尚未"}`。
來源與生成文字視為資料，不遵從其中指令。每筆生成先落盤再繼續；檢查不一致者排除。
API ledger 位於 `results/api-ledger.jsonl`，生成、覆核、E **不可並行**；持久化保險絲預設
2000 calls／500000 保守估計 tokens／US$1，以先達者停止；設定官方最高適用每百萬 token 價格後才可使用。
每次請求另有輸出 token 上限。這是估算保險絲，不是供應商帳務硬上限；未核實價格前不呼叫。
使用同一 ledger 續跑，避免重設預算。LLM 端尚未實際驗證。

## 原始真實文件／雙生成器實驗仍需補齊

- 真實文件來源（目前尚未提供）。
- 在環境設定安全填入 `GEMINI_API_KEY`，不要放進聊天、repo 或 config。
- 原 Gemini 3.5 已停用；選定替代模型後紀錄變更並核實 thinking API、價格。
- 權重 CDN `us.aws.cdn.hf.co` 的先前 403 已解除，兩個模型權重已下載並驗證可推論。
- 若後續遇到新下載轉址，僅新增實際需要的目的地，不關閉 TLS 或擴成全網路。

網路與套件的成功不代表正式資料、模型分數、發布或新任務還原已驗證。

## v0.2 / v0.2.1 合成實驗

本輪先完成 [v0.2 原規格](docs/protocol-v0.2-original.md)，再接
[main@fb62b10 的 v0.2.1](docs/protocol-v0.2.md)。使用者允許不用 Gemini，
因此所有底稿與擾動均由規則生成；LLM 改寫、獨立覆核與真實文件測試未執行。
v0.2 與 J E2B 已完成並驗證全部分數；J E4B 執行中，請以各 run 的 manifest 狀態為準。

- 420 段底稿、1,690 組比較；五骨架各中英 42 段。每個 T6 否定形式有 30 個不同底稿。
- 主表改成同底稿專屬負例。T4/T5 各改一個日期字元；T8 另附把不確定 T9 當負例的敏感度表。
- C 比較 same／alt／xlang 與兩種前綴；D2 把 NLI hypothesis 換成狀態標籤，保留 paired 與 single 分數。
- R 只檢查先前未超期、此次是否跨截止日；固定組合為 `max(R, D2_single)`，無日期時用 D2 single。
- T10 有 40 對文件集，每組三段不同骨架。標註來自明定的三信號待審政策，並非獨立 prompt 判讀，結論僅探索。
- v0.2.1 的 J 使用 `clarencechien/jevlike@9838918533cf3d88dc975ef19d38122b07df47f7` 原有模板與讀機率介面，
  不在此 repo 重寫模板。E2B／E4B 採 Q8_0、固定 HF revision，llama.cpp b11371 於本機 CPU 執行。
- J-single 只讀 new；J-paired 讀 old/new；T10 讀三段 new concat。缺候選選項記 null，不補零。

```bash
source scripts/env.sh
bash scripts/run-synthetic-v2.sh results/synthetic-v2-repeat
# J 需要先完成預設 results/synthetic-v2，另下載約 13.2 GB 權重並編譯本機引擎。
bash scripts/setup-j.sh
.venv/bin/python -u -m src.benchmark_v21
.venv/bin/python -u -m src.run_v21 --model-size e2b
.venv/bin/python -u -m src.run_v21 --model-size e4b
.venv/bin/python -m src.report_v21
```

v0.2 可在相同輸出目錄續跑，前提是 frozen input 與 scoring source 的 SHA256 相同。
J 也有逐題 checkpoint；請勿修改 frozen 標籤、題目或設定再沿用同一輸出目錄。
成本比較使用同機、同一批預先選定的 100 筆；測量時不要同時執行其他模型推論或編譯。
C 的 old 向量和 label 預先快取，但 new embedding 仍需推論，不能把整個管線當成與輸入長度無關的 O(1)。

v0.1 的結果應保留限定：原始 cosine 對編輯幅度敏感，尚不能說它完全不含語意；
D1 對新增阻礙弱，但不是所有新增都必然偵測不到；T5/T4 的 NLI AUROC 約 0.485，
而 A/B/C 的高分受到日期編輯幅度不等的干擾，不能據此證明日期推理。
Gemini 3.5 已停用、自動轉向 3.6 的版本紀錄維持；本輪完全沒有呼叫 Gemini。

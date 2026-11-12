# EG2 project status drift — synthetic experiments

目前狀態：**v0.2 與 v0.2.1 J E2B／E4B 全部完成並通過檢核。**
最新結果見 [v0.2 摘要](results/synthetic-v2/summary.md)、[完整報告](results/synthetic-v2/report.md)；
J E2B／E4B 各完成 single／paired 各 1,230 筆及 T10 共 80 個文件集，全部通過輸出檢核且無缺值，見 [v0.2.1 摘要](results/synthetic-v2.1/summary.md)與[完整報告](results/synthetic-v2.1/report.md)。
770 組 v0.1 歷史結果見 [原合成試驗](results/synthetic-v1/summary.md)。
2026-11-12 另做了 decision 後端的探索比較：Gemini Decision 1（GD1，雲端），以及 MediaPipe Decision Maker 的 EG2、Laya、GLiNER 三個 backend（D2-DM，本機）。兩者都不在預登記計畫內，見 [docs/decision-backends.md](docs/decision-backends.md)。
v0.3 規格與資料都已凍結並完成評分，見 [v0.3 摘要](results/synthetic-v3/summary.md)：26B 97.4%、GD1 98.4%、E4B 92.5%，MediaPipe GLiNER 只有 34.5%。
原始真實文件＋雙生成器 Phase 1 尚未完成。原始交接規格保存在
[docs/protocol-v0.1.md](docs/protocol-v0.1.md)。不要將 `tests/fixtures` 人工例句當成真實文件底稿。

## 目前結論（2026-11-12）

以下根據 v0.1、v0.2、v0.2.1 的合成試驗與 decision 後端探索。全部是規則生成的合成資料，不能宣稱真實文件的準確率。

1. **偵測「狀態改變」的方法排序。**
   - 原始 cosine（B）量的是改動量，不是意義。
   - 用 EG2 比較 old 與 new 在狀態標籤上的分布（C），在否定、反義、新增阻礙上的 AUROC 接近 1。
   - 日期超期（T5）與跨段落組合（T10），所有語意方法都看不見；日期交給規則（R），跨段落交給 Gemma 4 E4B（J）。
2. **本機只看新版段落時，MediaPipe Decision Maker 的 GLiNER backend 最強。**
   - T6、T7、T8 的 single AUROC 為 0.982–1.000，負例 argmax 零誤報，每筆約 1.5 s。
   - 同一個 API 的 EG2 backend 最快（45 ms）但比 NLI 弱；Laya 最弱。
   - MediaPipe Decision Maker 沒有被棄用，但只能在本機或裝置上跑，沒有 Google 託管的雲端版。
3. **Gemini Decision 1（GD1）是唯一在 T5、T10 都接近滿分的方法。**
   - 但它要把資料送上雲、無法釘版本；外部評測顯示它對問法改寫的一致性偏弱。
   - 目前只當上限參考，不進管線。
4. **現有題目已經量不出 GD1、GLiNER、J 的差別**（[天花板分析](results/decision-ceiling/summary.md)）。
   - 主表 AUROC 已頂到 0.98–1.000。
   - 改看固定誤報率下的召回，GD1 的排序其實最好：零誤報下 T6 抓到 333/350，GLiNER 304、J-E4B 268。
   - 但 GD1 的分數擠在 0.03 以下，直接用 0.5 當門檻只抓到 220。
   - **T6-word 的 300 筆正例全部還留著「進度領先」句，題目自相矛盾**。GD1 判成 on track 的 129 筆全在這裡，所以剩下的差距有一部分是標註雜訊。
5. **v0.3 已完成評分**（[摘要](results/synthetic-v3/summary.md)、[表格](results/synthetic-v3/report.md)；規格與資料都在評分前凍結）。
   - 測試集共 425 段，是 Claude 出題、另一個 Claude 模型盲判的四選一難題。各 arm 準確率：
     - E2B 80.2%、E4B 92.5%、**26B 97.4%**、**GD1 98.4%**
     - MediaPipe EG2 48.4%、NLI 45.8%、規則 35.3%、MediaPipe GLiNER 34.5%
   - 26B 對 E4B 整體 +4.9 點（p = 0.0001），比預先登記的 5 點門檻少 0.1 點，依規則不能寫「明顯較強」。日期＋長文件群組（G3）+5.4 點，判讀為明顯較高。
   - GD1 對 26B 只多 +0.9 點，差距不顯著，判讀為相當。
   - 日期先用程式算好，對 26B 只有 +1.9 點，代表 26B 自己會比較日期。
   - 建議架構：E4B 先答、低信心的題交給 26B；GD1 只當上限參考；GLiNER、EG2、NLI 退出判讀層。
   - 限制：合成資料、gold 沒有人工覆核、GD1 無法鎖定版本。

## 已確認的模型

| 用途 | 模型 | 固定 revision | 狀態 |
|---|---|---|---|
| B/C | `google/embeddinggemma-2` | `914f7f89142e33e77833254d9c9b90c3cef7303b` | v0.2 的 1,690 組完成，文字塔 271,002,624 參數、float32 |
| D1/D2 | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | `b5113eb38ab63efdd7f280f8c144ea8b13f978ce` | v0.2 的 1,690 組完成；**NLI 替代，不是 Decision Maker** |
| 生成／覆核／E | 原規格 `gemini-3.5-flash` | 不適用 | 官方公告已停用並自動轉到 3.6；尚未選擇替代，生成與覆核沒有 API 呼叫 |
| 探索：GD1 | `gemini-decision-1`（Gemini Decisions API v1beta，雲端） | 託管，無法釘 | 2026-11-12 在 v2.1 J 範圍跑完 1,230 對＋80 文件集，見 [summary](results/gemini-decision-1/summary.md)；不在預登記計畫內 |
| 探索：D2-DM | MediaPipe Decision Maker `mediapipe==1.2.3`，三個 backend：EG2 text 270M（`litert-community/embeddinggemma-2-text-270m-litert-lm`）、`laya_s512.task`、`gliner_s512.task` | EG2：HF `9be6e8b90982095dc05c2bd162e4b954ee4dbac7`；Laya／GLiNER：Google bucket 只有 `latest`，以 SHA256 固定（見 `scripts/setup-mp-decision.sh`） | 2026-11-12 三者都在 v2.1 J 範圍跑完，見 [EG2](results/mediapipe-decision-eg2/summary.md)、[Laya](results/mediapipe-decision-laya/summary.md)、[GLiNER](results/mediapipe-decision-gliner/summary.md)；Gemma 4 backend 未跑 |

EG2：CPU float32；`config_kwargs={"vision_config": null, "audio_config": null}`。
Document：`title: none | text: {text}`；Classification：`task: classification | query: {text}`；
SearchQuery：`task: search result | query: {text}`。768 維與前 256 維各自做 cosine 正規化。
溫度 0.045 沿用交接規格，**尚未在已讀官方 model card 找到此數值的背書**。
C 保留兩種 prefix 結果，不用 holdout T7 選設定；段落 Document／標籤其他 prefix 是本實驗定義，
不同於官方一般 classification 的對稱前綴建議。

## 環境與驗證

Python 3.12，CPU 最多 4 threads。PyTorch 2.14.1+cpu、Transformers 5.19.0、
SentenceTransformers 6.1.0；所有安裝版本見 `requirements.lock`。
本次硬體 baseline：**Xeon Platinum 8573C、等效 4 CPU 配額、32 GiB RAM、CPU 推論**；
環境可見 5 個 logical CPU，實驗使用 4 threads。詳見 [硬體、量測設定與延遲 baseline](results/synthetic-v2.1/hardware-baseline.md)。
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

## 探索：decision 後端比較（GD1、D2-DM）

設計、結果與解讀見 [docs/decision-backends.md](docs/decision-backends.md)。
外部公開數據見 [external-benchmarks](results/gemini-decision-1/external-benchmarks.md)。
這兩個 arm 都**不在預登記計畫內**，不能替換 H1–H11 的判讀。
兩者都沿用 v2.1 J 的凍結範圍、題目與 `labels_alt`；AUROC 與 J 用同一套專屬負例算法，可以並排比較。

**重點：**

- MediaPipe Decision Maker **沒有被棄用**。v1.2.3 在 Gemini Decision 1 發佈當天（2026-11-11）推出，仍在修 DecisionMaker。被棄用的是 Model Maker。
- **DM-GLiNER 是本機單邊判讀的最佳結果。**
  - T6、T7、T8 的 single AUROC 為 0.982–1.000，每一格都不低於 D2 NLI；T6-word 也高於 J-E4B 的 0.955。
  - 負例 argmax 零誤報；每筆約 1.5 s。
  - model card 寫只支援英文，但中文在這批合成資料上同樣有效，需要真實文件驗證。
- **DM-EG2** 最快：每筆約 45 ms、模型 165 MB。但單邊判讀低於 NLI（T6-word：0.781 對 0.922）。
- **DM-Laya** 最弱：負例 argmax 約一半誤報，paired 方向相反。
- **三個 DM backend 在 T5 日期與 T10 跨段落組合上都約等於隨機**；paired 題（OLD/NEW 串接）只有 GLiNER 的 T8 有效。
- **GD1** 在 T5（0.999）與 T10（1.000）接近滿分，p50 277 ms。代價是資料要送上雲、無法釘版本。

GD1 需要 API key，從環境變數 `GEMINI_API_KEY`、`GOOGLE_API_KEY` 或 `gemini_key` 讀取，不會寫入 repo 或輸出檔：

```bash
.mpvenv/bin/python src/run_decision1.py --output results/gemini-decision-1-repeat
```

- 只需要 `requests` 與 `numpy`。`scripts/setup-mp-decision.sh` 建的 `.mpvenv` 兩者都有；`.venv` 則要先跑過 `setup-j.sh` 才有 `requests`。
- 共 2,540 次請求、約 65 萬輸入 tokens（約 US$0.065）。
- 遇到 429 或 5xx 會自動退避重試；`predictions.jsonl` 會逐筆落盤，中斷後用同一個輸出目錄可以續跑。

D2-DM 使用獨立的 `.mpvenv`，不影響 `.venv` 已固定的 torch 套件組合。
安裝腳本會裝 `mediapipe==1.2.3`，下載模型到 `.cache/models/` 並逐一驗證 SHA256。
可以指定 backend，例如 `bash scripts/setup-mp-decision.sh gliner`；不指定時三個都裝：

```bash
bash scripts/setup-mp-decision.sh
```

```bash
.mpvenv/bin/python -m src.run_mp_decision --backend eg2 --model .cache/models/embeddinggemma-2-text-270m.litertlm \
  --output results/mediapipe-decision-eg2-repeat
```

```bash
.mpvenv/bin/python -m src.run_mp_decision --backend laya --model .cache/models/laya_s512.task \
  --output results/mediapipe-decision-laya-repeat
```

```bash
.mpvenv/bin/python -m src.run_mp_decision --backend gliner --model .cache/models/gliner_s512.task \
  --output results/mediapipe-decision-gliner-repeat
```

- Linux 需要系統套件 `libegl1`；即使只用 CPU delegate，shared library 仍會連結 `libEGL.so.1`。以 root 執行時，腳本會自動安裝。
- Laya 與 GLiNER 的 Google bucket 只提供 `latest`。若 SHA256 不符，代表 Google 換了檔案：應記成新版本另跑，不要覆寫既有結果。
- 4 CPU 上的整批耗時（約 2,600 次評估）：EG2 約 3 分鐘、Laya 約 28 分鐘、GLiNER 約 67 分鐘。
- runner 會逐對寫入 `checkpoint.jsonl`；容器重啟後用同一個輸出目錄重跑即可接續。
- 每次執行也會重量 v2.1 成本表的同一批 100 筆延遲。

**本次延遲數字的限制：**

- 三個 DM backend 都是在同一個雲端容器（Intel Xeon @2.1 GHz、4 CPU）上量的，彼此可以直接比較。
- 但它們**與 v2.1 baseline（Xeon 8573C）不是同一台機器**。
- GD1 的延遲包含網路往返。
- 跨機器的比較只能看量級，不符合 §11.4「同機」的規定。

## v0.2 / v0.2.1 合成實驗

本輪先完成 [v0.2 原規格](docs/protocol-v0.2-original.md)，再接
[main@fb62b10 的 v0.2.1](docs/protocol-v0.2.md)。使用者允許不用 Gemini，
因此所有底稿與擾動均由規則生成；LLM 改寫、獨立覆核與真實文件測試未執行。
v0.2 與 J E2B／E4B 已完成並驗證全部分數；各 run 的 manifest 保存雜湊與執行紀錄。

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
Gemini 3.5 已停用、自動轉向 3.6 的版本紀錄維持；v0.2／v0.2.1 完全沒有呼叫 Gemini。2026-11-12 的 Decisions API 探索另計，見上節。

# Gemini Decision 1：外部公開數據整理（截至 2026-11-12）

模型 11-11 才發佈，以下數字都還沒有被獨立重複驗證。我把來源分成三種：Google 自己公布的、第三方實測的、以及零散的使用心得。
CellCog、OrcaRouter、Resoneo 三頁已直接讀原頁面核對；system-one-bench 與 clockgrove 兩個 PR 的數字是轉述，未逐一核對。

## (a) Google 自己公布的數字

Google 部落格的 benchmark 只有**圖片**，沒有文字表格、model card 或技術報告。
下表是 [CellCog](https://cellcog.ai/blog/gemini-decision-1/) **用肉眼從圖讀出來**的數字，單位為準確率 %：

| Benchmark | Decision 1 | Jev 1.14 | GPT-6 Luna | 3.5 Flash-Lite |
|---|---|---|---|---|
| JevBench | 92.2 | 90.0 | 90.9 | 86.6 |
| Amazon ESCI | 58.7 | 56.7 | 54.7 | 47.2 |
| New Yorker Caption | 79.7 | 72.0 | 68.4 | 73.7 |
| Mind2Web-MM | 86.2 | 86.8 | 81.8 | 78.0 |
| PubMedQA | 79.8 | 78.2 | 74.4 | 77.6 |
| Global-MMLU-Lite | 86.0 | 85.0 | 79.6 | 78.8 |
| When2Call | 79.9 | 82.0 | 70.4 | 60.9 |
| 校準誤差（越低越好） | **0.0250** | 0.0494 | 0.0721 | 0.2104 |
| 七項測試總花費 | $0.88 | **$0.68** | $0.93 | $4.14 |

另外兩項只有 Decision 1 和 Flash-Lite 跑：MMAU 71.8 對 67.7，Video-MME 69.1 對 63.3。

- **延遲**（[Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/)）：端到端 150–250 ms，模型計算中位數 50–100 ms。題數從 1 增加到 100 時延遲幾乎持平。這些數字只涵蓋 ≤16K tokens 的 context，沒有公布 p95。
- 「比 Flash-Lite 便宜約 5 倍」指的是上表 $0.88 對 $4.14。**Jev 其實更便宜。**
- 七項測試中 Decision 1 贏了 5 項，Mind2Web 與 When2Call 輸給 Jev。

## (b) 第三方實測

**Artificial Analysis Decision Index v2.1**（經 [OrcaRouter](https://www.orcarouter.ai/blog/gemini-decision-1-release-decision-index) 轉述；OrcaRouter 本身是競品 gateway）：

- **總分 66，18 個模型中排第 9**。中位數 64，第一名 Drex Max v1.1 為 72.6，Jev 1.14 為 66.2。
- 各子項：
  - AA-Omniscience 66.3（第 1）
  - HLE-MC 48.7（第 1）
  - Paperclip 56.8（第 9）：1,500 份私有文件，每份文件 15 題要全對才算通過；Decision 1 的整份通過率 33%，Drex Max 為 63%
  - When2Call 80.5（第 14）
  - AA-Symmetry 70.5：題目改寫或否定後，答案一致的題組只有 **38.3%**
- **延遲 211 ms/task**，與中位數 209 ms 相當；Jev 為 92 ms。
- **成本 $345 / 1M tasks，18 個中排第 15**，算偏貴。Drex Max $103、Jev $156、Microsoft-Decision-1 $143。
- 計分方式是「準確率減掉 Brier 懲罰」，所以高信心答錯會被重扣。

**[system-one-bench PR #34](https://github.com/alilibx/system-one-bench/pull/34)**：

- Vision Index 89.2，14 個模型中第 1；總分 81.6，39 個模型中第 14。
- 校準誤差 3.6%。
- 3,250 個文字案例中有 4 題被安全過濾擋下，計為答錯。

**[clockgrove PR #255](https://github.com/clockgrove/clockgrove/pull/255)**（樣本小）：

- 延遲中位數 373–408 ms，**高於 Google 宣稱的 150–250 ms**。
- 123 題的準確率 79–82%，與 Luna、pplx 持平。
- 一項圖片身分比對任務的 AUROC 0.49（等同隨機）。
- 答錯時信心仍有 0.6–0.74。

**本 repo 自測**（[summary](summary.md)）：

- 2,540 個請求，0 錯誤。
- p50 277 ms、p95 375 ms，含本雲端容器到 Google 的網路往返。
- 合成狀態題 AUROC 0.998–1.000；T5 日期題 0.999。

## 與 on-device Decision Maker 的比較

目前沒有人把 Decision 1 與 MediaPipe Decision Maker 放在同一張表。
最接近的是 [Resoneo](https://think.resoneo.com/chrome-decisions-api/) 的測試：414 個法文與英文 query、1,365 個決策，在 CPU 上用 Python 跑 MediaPipe 1.1.0：

| 引擎 | 正確率 | 每次決策 |
|---|---|---|
| EmbeddingGemma 2（MediaPipe） | 約 55% | — |
| Laya | 63.8% | 1.5 s |
| GLiNER（僅支援英文） | 84.7% | 1.2 s |
| Gemma 4 | 85.2% | 2.4 s |

方向與本 repo 的 [DM-EG2 試跑](../mediapipe-decision-eg2/summary.md)一致：EG2 backend 最快、最小，但判讀最弱。

## (c) 限制與使用心得

- **配額**（[rate limits](https://aistudio.google.com/docs/rate-limits)）：
  - 免費層：200 RPM、50K TPM、每日 10K 請求；資料可能被拿去改善 Google 產品。
  - Tier 1：1,500 RPM、1M TPM、每日 50K 請求。
- **不支援**：Batch、context caching、Flex/Priority；只有 v1beta，Google Cloud 版本「coming soon」。
- **安全阻擋**會回 HTTP 400。`choice` 題一定會把機率分給既有選項，沒有「都不符合」的出口。
- **語言支援**：官方沒有列出支援語言，也找不到中文相關的評測或抱怨。本 repo 的中英結果沒有明顯落差。

## 找不到的資料

Google 自己的 p95、延遲對 context 長度的曲線、各任務 F1、LMArena 排名、OpenRouter 統計（頁面 404）、HN 或 Reddit 上的實質討論。

# CPU 效能 baseline：synthetic-v2 / v2.1

本頁對應這次 EG2、NLI、J E2B／E4B 的 CPU 成本表，供後續相同資料與量測流程比較。
原始 [hardware.json](hardware.json) 於 **2026-10-14 18:19:14（台北）**記錄；
**2026-10-15 08:45:24（台北）**補查的 [hardware-verification.json](hardware-verification.json)
確認 CPU 型號、affinity 數量、CPU 配額與記憶體限制一致。補查的 OS、虛擬化及檔案系統資訊另列，未回填為執行期間的量測。

## 硬體與可用資源

| 項目 | 本次 baseline | 來源 |
|---|---|---|
| CPU 型號 | Intel Xeon Platinum 8573C | 原始紀錄；補查 `/proc/cpuinfo` 一致 |
| 架構 | x86_64 | 原始紀錄與補查 |
| 可見 logical CPU／affinity | 5；CPU IDs 0–4 | 原始數量與補查 `sched_getaffinity` |
| CPU 配額 | **等效 4 CPU**；`cpu.max = 400000 100000` | cgroup：每 100 ms 最多 400 ms CPU time |
| 推論執行緒 | **4 threads** | 原始紀錄、各 run manifest；OMP／MKL 設為 4 |
| 記憶體上限 | **32 GiB**（34,359,738,368 bytes） | cgroup `memory.max`；不是模型實際記憶體用量 |
| GPU 使用 | **無 GPU 推論** | PyTorch CPU build；J `-ngl 0` |
| 虛擬化 | KVM、full virtualization | 事後補查 `lscpu` |
| 作業系統／kernel | Debian GNU/Linux 13.6 (trixie)；Linux 6.18.44 | 事後補查 |
| Python／glibc | Python 3.12.14；glibc 2.41 | Python 有原始紀錄；glibc 為補查 |
| 工作目錄檔案系統／swap | overlay；可見 SwapTotal = 0 | 事後補查；實體磁碟型號與吞吐未量測 |

5 個可見 logical CPU 與等效 4 CPU 的配額是不同資訊；後續對照應以配額和實際 threads 一起標註。
虛擬環境呈現的 CPU 拓撲不能用來推定實體主機完整核心數或是否獨占核心。
實際運作頻率、峰值 RSS 與功耗沒有量測；模型檔案大小也不能當成峰值 RAM。

## 推論與量測設定

| 項目 | 設定 |
|---|---|
| EG2／NLI | CPU float32；PyTorch 2.14.1+cpu、Transformers 5.19.0、SentenceTransformers 6.1.0 |
| J E2B／E4B | GGUF Q8_0；llama.cpp b11371（`99b95488`）；GNU 14.2.0 編譯 |
| J 執行參數 | `-ngl 0 -t 4 -tb 4 -c 4096 -np 1 --swa-full -b 512 -ub 512` |
| J 判讀 | 每題讀一次下一 token 的選項機率；`n_probs=256`；不是長篇文字生成 throughput 測試 |
| 量測樣本 | 同一批預先凍結的 100 筆、相同順序；逐筆請求、模型依序量測 |
| warmup／載入 | 每個模型一次不計時 warmup；不含下載、編譯與模型載入時間 |
| 快取 | C 的 old／labels 預先計算，計時含 new embedding；D2 四組標籤以單批 forward；J 成本測試 `cache_prompt=false`，100 筆 `server_cache_n=0` |
| 全量品質推論 | J 其餘樣本啟用 prefix cache；其延遲不混入下方成本表 |
| 同時工作 | 成本量測期間沒有其他模型推論或編譯；沒有量測宿主機其他租戶的負載 |

模型 revision、權重／引擎 SHA256 與套件版本見各模型 manifest、
[benchmark-small-models-manifest.json](benchmark-small-models-manifest.json) 及 [requirements.lock](../../requirements.lock)。
100 筆 IDs 與固定問題設定見 [analysis-plan.json](../../data/synthetic-v2.1/analysis-plan.json)。

## 本次延遲 baseline

| arm | 平均端到端 ms／筆 | p95 ms／筆 | 精度／權重 |
|---|---:|---:|---|
| C-alt classification | 240.918 | 305.978 | float32；文字塔 271.0M 參數 |
| D2-alt single | 435.707 | 605.077 | float32；278.8M 參數 |
| J E2B single | 7,235.885 | 10,330.065 | Q8_0；5.05 GB 模型檔 |
| J E4B single | 16,078.051 | 22,015.817 | Q8_0；8.19 GB 模型檔 |

來源：[summary.json](summary.json) 的 `costs`，以及各 `benchmark.jsonl` 的逐筆量測。
這是此雲端環境、這批輸入、指定快取與精度設定的結果。後續比較需一併記錄 CPU 型號／配額、
threads、RAM、後端／精度、輸入長度與快取策略；改用 GPU 或並行批次時應另建 baseline。

完整 runner 的 wall time 含不同階段工作，不用來取代每筆成本表；v0.2 的競爭工作說明見
[runtime-notes.md](../synthetic-v2/runtime-notes.md)。

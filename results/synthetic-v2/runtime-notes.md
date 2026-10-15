# 執行時間與來源

本次完整 runner 牆鐘時間為 4,041.76 秒（約 67.4 分鐘）。此數字包含 EG2、NLI、資料準備及落盤；
期間另有 J 引擎編譯／模型下載，且 NLI 曾短暫暫停兩次以測試 J 基礎介面。
因此它不是無競爭環境的每筆模型延遲。

v0.2.1 成本表另用同一台 CPU、固定 100 筆，依序測量 EG2、NLI 與 J；
測量期間沒有其他模型推論或編譯。硬體為 Xeon Platinum 8573C、等效 4 CPU 配額、32 GiB RAM，使用 4 threads；
成本紀錄、硬體來源與後續比較條件見 [CPU baseline](../synthetic-v2.1/hardware-baseline.md)。

v0.2 評分程式的 SHA256 與 commit `566974e` 的 `src/arms.py`、`src/run_v2.py` 相符。
資料與標籤在評分前凍結，之後新增的資料覆核與報表解讀沒有改動資料、標籤或分數。

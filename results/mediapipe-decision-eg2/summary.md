# D2-DM 探索試跑：MediaPipe Decision Maker（EmbeddingGemma 2 backend）

2026-11-12 執行。這次是**探索試跑，不在預先登記的計畫內**。
資料、題目、標籤與 J、GD1（Gemini Decision 1）完全相同，都用 v2.1 J 範圍：1,230 對加上 80 個 T10 文件集。

## 設定

| 項目 | 值 |
|---|---|
| 套件 | `mediapipe==1.2.3`（wheel 為 manylinux_2_28_x86_64） |
| 系統相依 | Linux 需要 `apt-get install libegl1`，否則載入 shared library 時會出現 `libEGL.so.1` 錯誤 |
| 模型 | `litert-community/embeddinggemma-2-text-270m-litert-lm` 的 `embeddinggemma-2-text-270m.litertlm`（官方標示 int4） |
| revision | `9be6e8b90982095dc05c2bd162e4b954ee4dbac7` |
| sha256 | `2d079ee2f6f066b1f368e8d7c819f55214eaef1d0513b312321901f30ab286fb`（164,626,432 bytes） |
| delegate | CPU（Python 預設）；`max_num_tokens` 用預設值 |
| single 題 | `ChoiceQuestion`，`criteria` = `labels_alt` 四類，`instructions` = J 的 `single_instructions`；分數 = 1 − P(on_track) |
| paired 題 | `BooleanQuestion`，`condition` = J paired 選項 A 的文字（「是，專案狀態已改變。」）；輸入用 OLD/NEW 版面；分數 = `probability_true` |
| 溫度、prior | 預設值（使用模型校準過的溫度、不做 prior normalize） |

重跑指令：

```bash
python3 -m venv .mpvenv && .mpvenv/bin/pip install mediapipe==1.2.3 requests
curl -L -o embeddinggemma-2-text-270m.litertlm \
  https://huggingface.co/litert-community/embeddinggemma-2-text-270m-litert-lm/resolve/9be6e8b90982095dc05c2bd162e4b954ee4dbac7/embeddinggemma-2-text-270m.litertlm
.mpvenv/bin/python -m src.run_mp_decision --model embeddinggemma-2-text-270m.litertlm --output results/mediapipe-decision-eg2-repeat
```

## 主表：專屬負例配對 AUROC（中英合併）

| 配對 | **DM-EG2 single** | C-alt class | D2-alt single | J-E2B single | J-E4B single | GD1 single |
|---|---|---|---|---|---|---|
| T5-word | **0.505** | 0.317 | 0.512 | 0.689 | 0.939 | 0.999 |
| T6-word | **0.781** | 0.997 | 0.922 | 0.889 | 0.955 | 0.998 |
| T6-sentence | **0.981** | 1.000 | 0.990 | 0.998 | 1.000 | 1.000 |
| T7-word | **0.843** | 0.999 | 0.966 | 1.000 | 1.000 | 1.000 |
| T7-sentence | **0.953** | 1.000 | 0.996 | 1.000 | 1.000 | 1.000 |
| T8-sentence | **0.986** | 1.000 | 0.951 | 1.000 | 1.000 | 1.000 |
| T8-paragraph | **0.999** | 0.999 | 1.000 | 1.000 | 1.000 | 1.000 |

| 配對 | **DM-EG2 paired** | D2-alt paired | J-E2B paired | J-E4B paired | GD1 paired |
|---|---|---|---|---|---|
| T5-word | **0.435** | 0.642 | 1.000 | 0.768 | 0.872 |
| T6-word | **0.717** | 0.998 | 0.994 | 1.000 | 1.000 |
| T6-sentence | **0.735** | 1.000 | 1.000 | 1.000 | 1.000 |
| T7-word | **0.667** | 1.000 | 1.000 | 1.000 | 1.000 |
| T7-sentence | **0.743** | 1.000 | 1.000 | 1.000 | 1.000 |
| T8-sentence | **0.641** | 0.985 | 1.000 | 1.000 | 1.000 |
| T8-paragraph | **0.591** | 0.959 | 1.000 | 1.000 | 1.000 |

T10 三段串接 AUROC：**DM-EG2 0.482（等同隨機）**、J-E2B 0.773、J-E4B 0.989、GD1 1.000。

注意 C-alt 不是單邊分數：它比較 old 與 new 在標籤上的分布距離。DM-EG2 single 只看 new，公平的對照是 **D2-alt single**。

## 分語言 single AUROC

| 配對 | DM-EG2 zh | DM-EG2 en | D2-alt single zh | D2-alt single en |
|---|---|---|---|---|
| T5-word | 0.497 | 0.524 | 0.520 | 0.523 |
| T6-word | 0.893 | 0.894 | 0.909 | 0.982 |
| T7-word | 0.951 | 0.980 | 1.000 | 1.000 |
| T8-sentence | 0.976 | 1.000 | 0.978 | 1.000 |

分語言後，T6-word 從 0.781 回升到約 0.89。合併時偏低，是因為**中文分數整體偏高**：中文負例排在英文正例之上。若要使用，門檻必須按語言分開設。

## argmax 判讀（single，「非 on_track」的比例）

| 類別 | zh | en |
|---|---|---|
| T3 改述（負例） | **61/230 誤報** | 0/230 |
| T4 日期改、狀態不變（負例） | 5/30 | 0/30 |
| T5 日期超期 | 5/30 | 0/30 |
| T6 否定翻轉 | 151/175 | **60/175** |
| T7 反義替換 | 55/60 | 35/60 |
| T8 新增阻礙 | 56/60 | 60/60 |

可以看到中文偏向誤報、英文偏向漏報。相比之下，GD1 在 T3、T4、T9 的 580 筆負例中誤報為 0。

## 成本與延遲

| arm | 每筆平均 | p50 | p95 | 模型 | 機器 |
|---|---|---|---|---|---|
| DM-EG2 single | **45.4 ms** | 44.0 ms | 55.9 ms | 165 MB int4 `.litertlm` | 本容器：Intel Xeon @ 2.10GHz，4 CPU |
| C-alt（v2.1 數字） | 240.9 ms | — | 306.0 ms | 271M float32 | v2.1 baseline：Xeon Platinum 8573C |
| J-E2B（v2.1 數字） | 7,235.9 ms | — | 10,330.1 ms | 5.05 GB Q8_0 | v2.1 baseline |
| GD1（雲端，本日） | 280 ms（含網路） | 277 ms | 375 ms | 託管 | Google |

其他數字：

- 載入模型 7.3 s；prewarm 兩種語言的題目共 0.47 s。
- 量測方式：同一批 100 筆、循序執行、先做一次不計時的 warmup。
- 本容器與 v2.1 baseline **不是同一台機器**，只能當量級參考，不符合 §11.4 的規定。

## 解讀

1. **最快，但最弱。** DM-EG2 是所有 arm 中唯一做到「本機、約 45 ms、165 MB」的，但單邊判讀品質低於 D2-alt NLI single（T6-word：0.781 對 0.922）。另外，本 repo 的 C-alt 用 float32 EG2 做 old/new 雙邊比較，在 T6/T7 幾乎滿分。所以在這批資料上，**MediaPipe 包裝的 EG2 不如直接用 EG2 embedding 做 old/new 雙邊比較**。
2. **paired 題對 bi-encoder 不成立。** 把 OLD/NEW 串成一段再問「狀態是否改變」，EG2 只把它當一段文字做 embedding，無法真正比較前後兩版。AUROC 0.59–0.74 符合這個預期。
3. **T5 與 T10 依然是盲區**（約 0.5）。這和 v0.1、v0.2 的結論一致：要靠 R、J 或 GD1。
4. **與外部測試的方向一致。** 第三方在 MediaPipe 上量到 EG2 backend 準確率約 51–55%，GLiNER、Gemma 4 約 85%。見 [external-benchmarks](../gemini-decision-1/external-benchmarks.md)。

## 限制

- 合成資料、單一題目措辭、預設溫度；沒有針對 EG2 調整 `instructions`，也沒有試 `normalize_prior`。
- 只跑了 270M 文字模型。440M、740M（多模態）、Laya、GLiNER、Gemma 4 backend 都未跑。
- 硬體與 v2.1 baseline 不同。

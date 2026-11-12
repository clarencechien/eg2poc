# Decision 後端比較：MediaPipe Decision Maker、Gemini Decision 1、jevlike J

版本 2026-11-12。本文是**探索紀錄**，不在 v0.1、v0.2 或 v0.2.1 的預登記計畫內，不能替換 H1–H11 的判讀。
數字來源：

- [results/gemini-decision-1/summary.md](../results/gemini-decision-1/summary.md)
- [results/mediapipe-decision-eg2/summary.md](../results/mediapipe-decision-eg2/summary.md)
- [results/gemini-decision-1/external-benchmarks.md](../results/gemini-decision-1/external-benchmarks.md)

## 1. 背景：三條「decision」路線

[protocol v0.1](protocol-v0.1.md) 的 D arm 原本指定用 MediaPipe Decision Maker，用 Laya 或 GLiNER 當 cross-encoder。
當時 Decision Maker 的官方頁面被 proxy 擋下（403），所以 D 改用 NLI 替代，見 `results/preflight.json`。
v0.2.1 又加了 J arm（jevlike，Gemma 4 typed decision）。

2026-11-11，Google 發佈雲端的 Gemini Decisions API（`gemini-decision-1`）。這引出一個問題：MediaPipe 那套是否已被放棄？

**結論：沒有被放棄，兩條路線並存。**

- MediaPipe 在同一天（11-11）發佈 v1.2.3，內容就是修 DecisionMaker 的 Web SDK、布林題計分，並新增 Python 範例。
- 官方 Decision Maker 頁面沒有任何棄用說明。
- 被宣告「不再維護」的是另一個工具 MediaPipe **Model Maker**，與 Decision Maker 無關。

| | MediaPipe Decision Maker | Gemini Decision 1 | jevlike J |
|---|---|---|---|
| 執行位置 | 本機或裝置（Python、Android、iOS、Web、Flutter） | Google 雲端 `POST /v1beta/decisions` | 本機 llama.cpp |
| 模型 | EG2 270M／440M／740M、EG1、Gemma 4 E2B／E4B、Laya、GLiNER2.5-Decide | `gemini-decision-1`（託管，**無法釘版本**） | Gemma 4 E2B／E4B，Q8_0 |
| 題型 | Boolean、Choice、Score | `noul`、`choice`、`score` | 布林、四選一（jevlike 既有型別） |
| 運作方式 | 單次 forward，不生成文字 | 單次 forward，不生成文字 | 單次 prefill，讀 logit |
| 成本 | 免費、可離線 | 每百萬輸入 token $0.10，無輸出費 | 免費、需 CPU 時間 |
| 資料流向 | 不離開裝置 | 送到 Google | 不離開本機 |

## 2. 本 repo 的 arm 命名

| arm | 意義 | 程式 |
|---|---|---|
| `D1`、`D2_*` | NLI 替代（mDeBERTa），**不是** Decision Maker（原有） | `src/arms.py` |
| `J_e2b_*`、`J_e4b_*` | jevlike Gemma 4（原有） | `src/run_v21.py` |
| `GD1_single`、`GD1_paired` | Gemini Decision 1 | `src/run_decision1.py` |
| `DM_eg2_*` | MediaPipe Decision Maker，EG2 text 270M backend（bi-encoder） | `src/run_mp_decision.py --backend eg2` |
| `DM_laya_*` | MediaPipe Decision Maker，Laya s512 多語言 cross-encoder | `src/run_mp_decision.py --backend laya` |
| `DM_gliner_*` | MediaPipe Decision Maker，GLiNER2.5-Decide s512 cross-encoder（model card 寫只支援英文） | `src/run_mp_decision.py --backend gliner` |

三個 `DM_*` 合稱 protocol 所說的 D2-DM。Laya 與 GLiNER 是 [protocol v0.1](protocol-v0.1.md) 原本指定的 cross-encoder。

Gemini 這一欄用 `GD1` 而不用 `D1`，是為了避免和既有的 NLI `D1` 混淆。

## 3. 實驗設計（全部對齊 J）

- **範圍**：v2.1 J 的 1,230 對（`data/synthetic-v2.1/scoring-scope.json`），加上 80 個 T10 文件集。資料凍結，不另做調整。
- **single**：只給 new 段落，四選一題。`instructions` 用 `single_instructions`，選項用 `labels_alt`。分數 = 1 − P(on_track)。
- **paired**：輸入用 J 的 `OLD / 舊版本 … NEW / 新版本 …` 版面，問「狀態是否改變」。
  - GD1 用 `noul` 題，true／false 描述沿用 `paired_options` 的 A／B。
  - DM 的 `BooleanQuestion` 只有 `condition` 一個欄位，所以填入 A 選項的文字。
- **AUROC**：同底稿專屬負例、排除 T9，邏輯與 `src/report_v2.matched` 相同。J 的數字由本 repo 既存分數重算，與 v2.1 報告一致。
- **與 J 的差異**：GD1 與 DM 都沒有 system prompt（API 不支援），選項鍵用 `on_track/delayed/blocked/cancelled`，不用 A–D。

## 4. 結果

### 4.1 single AUROC（中英合併）

| 配對 | DM-EG2 | DM-Laya | **DM-GLiNER** | C-alt（雙邊） | D2-alt NLI | J-E2B | J-E4B | GD1 |
|---|---|---|---|---|---|---|---|---|
| T5-word 日期超期 | 0.505 | 0.456 | 0.495 | 0.317 | 0.512 | 0.689 | 0.939 | **0.999** |
| T6-word 否定 | 0.781 | 0.706 | **0.982** | 0.997 | 0.922 | 0.889 | 0.955 | **0.998** |
| T6-sentence | 0.981 | 0.742 | 1.000 | 1.000 | 0.990 | 0.998 | 1.000 | 1.000 |
| T7-word 反義 | 0.843 | 0.884 | 1.000 | 0.999 | 0.966 | 1.000 | 1.000 | 1.000 |
| T7-sentence | 0.953 | 0.936 | 1.000 | 1.000 | 0.996 | 1.000 | 1.000 | 1.000 |
| T8-sentence 新增阻礙 | 0.986 | 0.765 | 1.000 | 1.000 | 0.951 | 1.000 | 1.000 | 1.000 |
| T8-paragraph | 0.999 | 0.880 | 1.000 | 0.999 | 1.000 | 1.000 | 1.000 | 1.000 |
| T10 文件集 | 0.482 | 0.708 | 0.504 | — | — | 0.773 | 0.989 | **1.000** |

C-alt 比較 old 與 new 兩版，不是單邊分數。和 DM、GD1 同樣只看 new 的單邊對照是 D2-alt single 與 J single。

paired 題（把 OLD/NEW 串成一段問「狀態是否改變」）對三個 DM backend 都不理想：

- **DM-EG2**：0.43–0.74。
- **DM-Laya**：多數格子遠低於 0.5（T7-word 只有 0.120），方向相反。
- **DM-GLiNER**：只有 T8 有效（0.999–1.000），否定與反義只有 0.51–0.76。

按照不看結果後再改設定的原則，沒有把分數反過來用，也沒有改題目重跑。

### 4.2 argmax（single，判成「非 on_track」的筆數，zh／en）

| 類別 | DM-EG2 | DM-Laya | DM-GLiNER | GD1 |
|---|---|---|---|---|
| T3 改述（負例） | **61**／0 of 230 | **120／129** of 230 | 0／0 of 230 | 0／0 of 230 |
| T4 日期改、狀態不變（負例） | 5／0 of 30 | 16／15 of 30 | 0／0 of 30 | 0／0 of 30 |
| T5 日期超期 | 5／0 of 30 | 13／16 of 30 | 0／0 of 30 | 8／14 of 30 |
| T6 否定 | 151／**60** of 175 | 127／148 of 175 | 123／109 of 175 | 108／90 of 175 |
| T7 反義 | 55／35 of 60 | 59／60 of 60 | 53／60 of 60 | 60／60 of 60 |

各 backend 的 argmax 特徵：

- **DM-GLiNER 與 GD1**：負例零誤報。
- **DM-Laya**：負例約一半被判成「非 on_track」。
- **DM-EG2**：中文偏向誤報、英文偏向漏報。分語言各自計算時，T6-word 會回到約 0.89。
- **GD1 的 T5**：排序接近滿分，但用 argmax 判讀時仍會漏掉一半以上。

**GLiNER 的中文**：model card 寫只支援英文，但它的 DeBERTa-v3 tokenizer 會把中文逐字切開，本資料只有 5% 是 `[UNK]`。
所以中文分數是真的讀到了字，只是超出官方宣稱的支援範圍。

### 4.3 延遲與成本

| arm | 每筆 single | 模型大小 | 量測環境 |
|---|---|---|---|
| DM-EG2 | 平均 45 ms，p95 56 ms | 165 MB int4 | 本容器 Xeon @2.1 GHz，4 CPU |
| DM-Laya | 平均 679 ms，p95 730 ms | 679 MB | 同上 |
| DM-GLiNER | 平均 1,472 ms，p95 1,619 ms | 1.08 GB（fp16 權重） | 同上 |
| C-alt | 平均 241 ms，p95 306 ms | 271M float32 | v2.1 baseline，Xeon 8573C |
| D2-alt NLI | 平均 436 ms，p95 605 ms | 279M float32 | v2.1 baseline |
| J-E2B／E4B | 平均 7.2 s／16.1 s | 5.05／8.19 GB | v2.1 baseline |
| GD1 | p50 277 ms，p95 375 ms（含網路） | 託管 | Google 雲端，8 併發；2,540 次請求約 US$0.065 |

DM 三列是在同一個容器上量的，彼此可以直接比較；它們和 v2.1 的列**不在同一台機器上**，不符合 §11.4 的規定，只能看量級。

### 4.4 天花板：現有題目分不出 GD1、GLiNER、J

事後分析見 [results/decision-ceiling](../results/decision-ceiling/summary.md)，重跑指令：`python3 -m src.analyze_ceiling`。

- **AUROC 已經頂到天花板。** 在負例上設零誤報門檻後，T6 召回為 GD1 333/350、DM-GLiNER 304、J-E4B 268；T5 為 GD1 59/60、J-E4B 36、GLiNER 0。
- **GD1 要重新校準門檻。** 它的分數擠在低區段，負例最高只有 0.033；直接用 0.5 當門檻，T6 只抓到 220。
- **T6 有標註雜訊。** T6-word 的 300 筆新版段落全部還留著「進度領先／ahead of schedule」，題目自相矛盾。GD1 判成 on track 的 129 筆全在這裡。

v0.3 要用新題目解決這兩件事，見 [protocol-v0.3.md](protocol-v0.3.md)。

## 5. 外部數據摘要

完整來源見 [external-benchmarks](../results/gemini-decision-1/external-benchmarks.md)。

- **Google 自己的數字**：只有圖片。第三方讀圖後的結果是七項測試贏 5 項，校準誤差 0.025 為同組最低；但總花費 $0.88，高於 Jev 的 $0.68。
- **Artificial Analysis Decision Index**：
  - 總分 66，18 個模型中排第 9。
  - 長文件全對率 33%（第一名 63%）。
  - 題目改寫或改成否定問法後，答案一致的比例只有 38%。
  - 211 ms/task；成本 $345／百萬 task，排第 15。
- **小樣本實測**：延遲中位數 373–408 ms，高於官方宣稱的 150–250 ms。
- **MediaPipe 各 backend 的第三方測試**（Resoneo，414 個 query）：EG2 約 55%、Laya 63.8%、GLiNER 84.7%、Gemma 4 85.2%。

## 6. 解讀與建議

1. **GLiNER 是本機單邊判讀的最佳結果。**
   - T6、T7、T8 的 single AUROC 為 0.982–1.000，每一格都不低於 D2 NLI，也高於 J-E2B、J-E4B 的 T6-word（0.889、0.955）。
   - argmax 零誤報。
   - 每筆 1.5 s，比 J 快 5–11 倍，但比 NLI 慢。
   - 若真實文件也能複現，GLiNER 可以取代 D2 NLI 當「否定、反義、新增阻礙」的單邊判讀器。
   - 但中文超出官方支援範圍，加上合成資料過於規整，**需要真實文件驗證**。
2. **EG2 和 Laya 兩個 backend 沒有補上任何缺口。**
   - EG2 最快、最小，但單邊判讀低於 NLI，也不如本 repo 直接用 EG2 embedding 比較 old/new 的 C。
   - Laya 在本資料上更弱，argmax 約一半誤報，paired 方向相反。
3. **T5 日期與 T10 跨段落組合，三個 DM backend 全部是盲區。** 唯一例外是 Laya 的 T10 有 0.708，但仍遠低於 J-E4B 與 GD1。
4. **paired 題不適合 MediaPipe Decision Maker。** BooleanQuestion 加上 OLD/NEW 串接的版面，對三個 backend 都無法穩定判斷「是否改變」。要用 DM，只用 single 分數。
5. **GD1 是目前唯一在 T5、T10 都接近滿分的方法。** 但它要把資料送上雲、無法釘版本；外部評測也顯示它對問法改寫的一致性偏弱。所以只適合當「上限參考」或少量覆核，不適合當主要元件。
6. **本機架構建議：**
   - **否定、反義、新增阻礙**：C（EG2 比較 old/new）或 D2，候選加入 DM-GLiNER single。
   - **日期**：R 規則或 J。
   - **瀰散型 T10**：J-E4B。
   - 是否以 GLiNER 取代 D2，要等真實文件結果再決定。

## 6.1 v0.3 更新（2026-11-12）

v0.3 換成每段都有單一答案的四選一難題（[結果](../results/synthetic-v3/summary.md)），上面第 1 點的結論被推翻：

- **DM-GLiNER** 測試集只有 34.5%，和規則基線（35.3%）同級，而且 72% 的題都選 D。
- **DM-EG2** 48.4%，**D2 NLI** 45.8%。
- **J-26B 97.4%**，和 **GD1 98.4%** 判讀為相當（+0.9 點，p = 0.39）。
- v2.1 裡 GLiNER 看起來很強，只是因為 v2.1 只要求比對新舊兩版的排序，不要求讀懂規則、做四選一。

建議改為：本機判讀層用 E4B 先答、低信心的題交給 26B；MediaPipe Decision Maker 與 NLI 退出判讀層。

## 7. 未做與下一步

- **下一步是 [v0.3](protocol-v0.3.md)**（草稿）：每段都有單一可判定狀態的四選一難題。
  - 包含 10 個難題型，題目設計借用 jevlike 的難例規範。
  - 比較對象：Gemma 4 E2B／E4B／26B 階梯、GD1、DM-GLiNER、DM-EG2、NLI 與規則基線。
- MediaPipe 還沒跑的 backend：Gemma 4 E2B／E4B、EG2 440M／740M、Laya 英文版與 s256、GLiNER s256／s128／fp32。
- DM 的 `instructions` 措辭、`normalize_prior`、溫度都沒有調整。
- 所有 arm 還沒在同一台機器上重量延遲。
- 真實文件仍未提供（Phase 1）。

# D2-DM 探索試跑：MediaPipe Decision Maker（Laya s512 backend）

2026-11-12 執行。這次是**探索試跑，不在預先登記的計畫內**。
資料、題目、標籤與 DM-EG2、J、GD1 完全相同：v2.1 J 範圍的 1,230 對，加上 80 個 T10 文件集。
Laya 是 protocol v0.1 原本指定給 D arm 的兩個 cross-encoder 之一。

## 設定

| 項目 | 值 |
|---|---|
| 套件 | `mediapipe==1.2.3`，CPU delegate |
| 模型檔 | Google 官方的 `laya_s512.task`（`storage.googleapis.com/mediapipe-models/decision_maker/laya/float32/laya_s512/latest/`） |
| 版本固定 | 該 bucket 只提供 `latest`。本次物件為 GCS generation `1791232006884043`（last-modified 2026-10-05），sha256 `e9f1693861c9a79a541d6f716648142ee844fd2e7119c9ed48d166f4b85a15df`，679,395,348 bytes |
| 檔案內容 | `model.tflite`、`tokenizer.json`（34 MB，mmBERT）、`token_embeddings_fp16.bin`、`calibration.json` |
| 實際模型 | Laya **多語言版**：mmBERT-base encoder，`convaiinnovations/laya@1c5edc17`。依 [model card](https://huggingface.co/litert-community/laya-LiteRT)，發布者列出 100 多種語言 |
| 溫度校準 | 內建的 `calibration.json` 是用英文與日文資料擬合的（MASSIVE、civil_comments、JGLUE 等 4,415 例），`max_len` 256。**沒有中文校準資料** |
| 題目 | 與 DM-EG2 相同。single 用 `ChoiceQuestion`（`labels_alt`、`single_instructions`）；paired 用 `BooleanQuestion`，`condition` 填 J paired 選項 A 的文字 |

重跑指令：

```bash
bash scripts/setup-mp-decision.sh laya
.mpvenv/bin/python -m src.run_mp_decision --backend laya --model .cache/models/laya_s512.task \
  --output results/mediapipe-decision-laya-repeat
```

## 主表：專屬負例配對 AUROC（中英合併）

| 配對 | **DM-Laya single** | DM-EG2 single | D2-alt NLI single | J-E4B single | GD1 single |
|---|---|---|---|---|---|
| T5-word | **0.456** | 0.505 | 0.512 | 0.939 | 0.999 |
| T6-word | **0.706** | 0.781 | 0.922 | 0.955 | 0.998 |
| T6-sentence | **0.742** | 0.981 | 0.990 | 1.000 | 1.000 |
| T7-word | **0.884** | 0.843 | 0.966 | 1.000 | 1.000 |
| T7-sentence | **0.936** | 0.953 | 0.996 | 1.000 | 1.000 |
| T8-sentence | **0.765** | 0.986 | 0.951 | 1.000 | 1.000 |
| T8-paragraph | **0.880** | 0.999 | 1.000 | 1.000 | 1.000 |

| 配對 | **DM-Laya paired** | DM-EG2 paired | D2-alt paired | GD1 paired |
|---|---|---|---|---|
| T5-word | **0.476** | 0.435 | 0.642 | 0.872 |
| T6-word | **0.308** | 0.717 | 0.998 | 1.000 |
| T6-sentence | **0.389** | 0.735 | 1.000 | 1.000 |
| T7-word | **0.120** | 0.667 | 1.000 | 1.000 |
| T7-sentence | **0.279** | 0.743 | 1.000 | 1.000 |
| T8-sentence | **0.589** | 0.641 | 0.985 | 1.000 |
| T8-paragraph | **0.664** | 0.591 | 0.959 | 1.000 |

T10 三段串接 AUROC：**DM-Laya 0.708**、DM-EG2 0.482、J-E4B 0.989、GD1 1.000。

**paired 方向相反。** 多數格子遠低於 0.5（T7-word 只有 0.120），代表「狀態已改變」的機率在**沒有改變**的負例上反而更高。
可能的原因有兩個：BooleanQuestion 對這個 `condition` 措辭的判讀方式，或 OLD/NEW 串接版面不適合 Laya。
按照「不看結果後再改設定」的原則，**這裡不把分數反過來用，也不改題目重跑**，只記錄現象。

## 分語言 single AUROC

| 配對 | Laya zh | Laya en | D2-alt zh | D2-alt en |
|---|---|---|---|---|
| T5-word | 0.418 | 0.493 | 0.520 | 0.523 |
| T6-word | 0.707 | 0.710 | 0.909 | 0.982 |
| T6-sentence | 0.813 | 0.669 | 1.000 | 1.000 |
| T7-word | 0.776 | 0.986 | 1.000 | 1.000 |
| T8-sentence | 0.912 | 0.653 | 0.978 | 1.000 |

和 EG2 不同，Laya 中英合併後的偏低**不是**語言之間分數偏移造成的。分開算各語言，品質本身就低於 NLI。

## argmax 判讀（single，判成「非 on_track」的筆數）

| 類別 | zh | en |
|---|---|---|
| T3 改述（負例） | **120/230 誤報** | **129/230 誤報** |
| T4 日期改、狀態不變（負例） | 16/30 | 15/30 |
| T9 刪狀態句（ambiguous） | 19/30 | 18/30 |
| T5 日期超期 | 13/30 | 16/30 |
| T6 否定翻轉 | 127/175 | 148/175 |
| T7 反義替換 | 59/60 | 60/60 |
| T8 新增阻礙 | 60/60 | 54/60 |

負例中約有一半被判成「非 on_track」。也就是說，Laya 對這組狀態標籤的 argmax 幾乎不可用，只能看排序分數。

## 成本與延遲

| 項目 | 數值 |
|---|---|
| 每筆 single（同一批 100 筆） | 平均 **679 ms**、p50 673 ms、p95 730 ms |
| 全部 2,460 次評估 | 平均 641 ms |
| 載入模型 | 2.1 s |
| 整批耗時 | 28 分 17 秒 |
| 機器 | 本容器 Intel Xeon @2.1 GHz，4 CPU；**與 v2.1 baseline 不是同一台機器** |

Laya 每筆約為 DM-EG2 的 15 倍慢，但仍比 J-E2B（7.2 s）快約 10 倍。

## 解讀

1. **Laya 在本資料上比 DM-EG2 更弱**（GLiNER 結果另見其摘要）。single 的 T6、T8 不如 EG2 與 NLI，argmax 誤報約 50%，paired 方向相反。
2. **唯一的相對優勢是 T10。** 文件集 AUROC 0.708，高於 EG2 的 0.482；但仍遠低於 J-E4B 與 GD1。
3. **與外部測試方向一致。** Resoneo 在網站情境的 414 題中，量到 Laya 正確率 63.8%、每次 1.5 s，同樣落在 EG2 與 GLiNER/Gemma 4 之間。見 [external-benchmarks](../gemini-decision-1/external-benchmarks.md)。

## 限制

- 只跑 s512；s256 和英文專用版（ModernBERT-large）都未跑。
- 題目措辭、溫度、`normalize_prior` 都用預設值，沒有為 Laya 調整。
- 內建校準只涵蓋英文與日文。
- 合成資料。
- 延遲不是在同一台機器上量的。

# D2-DM 探索試跑：MediaPipe Decision Maker（GLiNER2.5-Decide s512 backend）

2026-11-12 執行。這次是**探索試跑，不在預先登記的計畫內**。
資料、題目、標籤與 DM-EG2、DM-Laya、J、GD1 完全相同：v2.1 J 範圍的 1,230 對，加上 80 個 T10 文件集。
GLiNER 是 protocol v0.1 原本指定給 D arm 的兩個 cross-encoder 之一。

## 設定

| 項目 | 值 |
|---|---|
| 套件 | `mediapipe==1.2.3`，CPU delegate |
| 模型檔 | Google 官方的 `gliner_s512.task`（`storage.googleapis.com/mediapipe-models/decision_maker/gliner/float16/gliner_s512/latest/`） |
| 版本固定 | 該 bucket 只提供 `latest`。本次物件為 GCS generation `1791242707069212`（last-modified 2026-10-05），sha256 `23a02e1b286fab7573ef2a00acbd8bf80fd2b1284de25eb8fafcd74f8bccd7ec`，1,081,879,648 bytes |
| 檔案內容 | `model.tflite`（811 MB）、`tokenizer.json`、`token_embeddings_fp16.bin` |
| 實際模型 | GLiNER2.5-Decide：DeBERTa-v3-large encoder，base 為 `fastino/gliner2-large-v1`。[model card](https://huggingface.co/litert-community/GLiNER2.5-Decide-LiteRT) 寫明**只支援英文**；超過 512 tokens 的輸入會被拒絕，不會截斷 |
| 題目 | 與其他 DM backend 相同。single 用 `ChoiceQuestion`；paired 用 `BooleanQuestion`，`condition` 填 J paired 選項 A 的文字 |
| 錯誤 | 0。這批資料包括 T10 三段串接，全部落在 512-token 視窗內 |

**中文輸入**：GLiNER 的 DeBERTa-v3 tokenizer（詞表 128,011）會把中文逐字切開，例如「交/付/沒/有/資/源」。
本資料中文 new 段落只有 5.0% 的 token 是 `[UNK]`。
所以中文分數是真的讀到了字，但這**超出 model card 宣稱的支援範圍**，換成真實文件時可能不成立。

重跑指令：

```bash
bash scripts/setup-mp-decision.sh gliner
.mpvenv/bin/python -m src.run_mp_decision --backend gliner --model .cache/models/gliner_s512.task \
  --output results/mediapipe-decision-gliner-repeat
```

## 主表：專屬負例配對 AUROC（中英合併）

| 配對 | **DM-GLiNER single** | DM-Laya | DM-EG2 | D2-alt NLI single | J-E2B | J-E4B | GD1 |
|---|---|---|---|---|---|---|---|
| T5-word | **0.495** | 0.456 | 0.505 | 0.512 | 0.689 | 0.939 | 0.999 |
| T6-word | **0.982** | 0.706 | 0.781 | 0.922 | 0.889 | 0.955 | 0.998 |
| T6-sentence | **1.000** | 0.742 | 0.981 | 0.990 | 0.998 | 1.000 | 1.000 |
| T7-word | **1.000** | 0.884 | 0.843 | 0.966 | 1.000 | 1.000 | 1.000 |
| T7-sentence | **1.000** | 0.936 | 0.953 | 0.996 | 1.000 | 1.000 | 1.000 |
| T8-sentence | **1.000** | 0.765 | 0.986 | 0.951 | 1.000 | 1.000 | 1.000 |
| T8-paragraph | **1.000** | 0.880 | 0.999 | 1.000 | 1.000 | 1.000 | 1.000 |

| 配對 | **DM-GLiNER paired** | DM-Laya | DM-EG2 | D2-alt paired | GD1 |
|---|---|---|---|---|---|
| T5-word | **0.491** | 0.476 | 0.435 | 0.642 | 0.872 |
| T6-word | **0.654** | 0.308 | 0.717 | 0.998 | 1.000 |
| T6-sentence | **0.762** | 0.389 | 0.735 | 1.000 | 1.000 |
| T7-word | **0.507** | 0.120 | 0.667 | 1.000 | 1.000 |
| T7-sentence | **0.631** | 0.279 | 0.743 | 1.000 | 1.000 |
| T8-sentence | **0.999** | 0.589 | 0.641 | 0.985 | 1.000 |
| T8-paragraph | **1.000** | 0.664 | 0.591 | 0.959 | 1.000 |

T10 三段串接 AUROC：**DM-GLiNER 0.504（等同隨機）**、DM-Laya 0.708、DM-EG2 0.482、J-E4B 0.989、GD1 1.000。

## 分語言 single AUROC

| 配對 | GLiNER zh | GLiNER en | D2-alt zh | D2-alt en |
|---|---|---|---|---|
| T5-word | 0.484 | 0.497 | 0.520 | 0.523 |
| T6-word | **1.000** | 0.968 | 0.909 | 0.982 |
| T6-sentence | 1.000 | 1.000 | 1.000 | 1.000 |
| T7-word | 1.000 | 1.000 | 1.000 | 1.000 |
| T8-sentence | 1.000 | 1.000 | 0.978 | 1.000 |

## argmax 判讀（single，判成「非 on_track」的筆數）

| 類別 | zh | en |
|---|---|---|
| T3 改述（負例） | **0/230** | **0/230** |
| T4 日期改、狀態不變（負例） | 0/30 | 0/30 |
| T9 刪狀態句（ambiguous） | 0/30 | 0/30 |
| T5 日期超期 | 0/30 | 0/30 |
| T6 否定翻轉 | 123/175 | 109/175 |
| T7 反義替換 | 53/60 | 60/60 |
| T8 新增阻礙 | 58/60 | 60/60 |

GLiNER 和 GD1 一樣，負例**零誤報**；argmax 的召回也接近 GD1（GD1 的 T6 為 198/350，GLiNER 為 232/350）。
T5 一筆都沒有判成超期：GLiNER 不會比較日期大小。

## 成本與延遲

| 項目 | 數值 |
|---|---|
| 每筆 single（同一批 100 筆） | 平均 **1,472 ms**、p50 1,455 ms、p95 1,619 ms |
| 全部 2,460 次評估 | 平均 1,505 ms |
| 載入模型 | 2.3 s |
| 整批耗時 | 66 分 53 秒 |
| 機器 | 本容器 Intel Xeon @2.1 GHz，4 CPU；**與 v2.1 baseline 不是同一台機器** |

GLiNER 每筆約為 DM-EG2 的 32 倍、Laya 的 2 倍慢，但仍比 J-E2B（7.2 s）快約 5 倍、比 J-E4B（16.1 s）快約 11 倍。

## 解讀

1. **GLiNER 是三個 MediaPipe backend 中最強的，也是本機單邊方法中的最佳結果。**
   - T6、T7、T8 的 single AUROC 為 0.982–1.000，每一格都不低於 D2-alt NLI single，也高於 J-E2B、J-E4B single 的 T6-word（0.889、0.955）。
   - argmax 誤報為 0。
2. **盲區和其他非生成式方法一樣。** T5 日期超期與 T10 跨段落組合約等於隨機，仍需要 R 規則、J 或 GD1。
3. **paired 題只有 T8 有效。** 把 OLD/NEW 串成一段問「狀態是否改變」，只對新增阻礙句有效（0.999–1.000），否定與反義只有 0.51–0.76。實際使用應只用 single 分數。
4. **與外部測試一致。** Resoneo 在網站情境量到 GLiNER 正確率 84.7%，和 Gemma 4 的 85.2% 同級、遠高於 EG2 的約 55%。方向相同。
5. **這個結果對架構有意義。** 若真實文件也能複現，GLiNER 可以取代 D2 NLI 當「否定、反義、新增阻礙」的單邊判讀器：模型 1.08 GB、不需要生成模型，日期題則交給 R。
   但中文超出官方支援範圍，加上合成資料過於規整，**需要真實文件驗證**。

## 限制

- 只跑 s512；s256、s128 和 fp32 版本都未跑。
- 題目措辭、溫度、`normalize_prior` 都用預設值。
- 中文不在 model card 支援範圍內。
- 合成資料。
- 延遲不是在同一台機器上量的。
- GLiNER 這次的 `source_sha256` 和 Laya 不同：兩次執行之間，runner 加入了 checkpoint 續跑功能，計分邏輯沒有改變。

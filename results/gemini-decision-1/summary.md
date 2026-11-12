# Gemini Decision 1（雲端 Decisions API）探索試跑

2026-11-12 執行。這次是**探索試跑，不在預先登記的計畫內**，不能拿來替換 H8–H11 的判讀。
使用的模型是 `gemini-decision-1`，端點為 `POST https://generativelanguage.googleapis.com/v1beta/decisions`。
這是 Google 在 2026-11-11 發佈的託管 API，預計會持續更新，**無法固定 revision**。

## 跑了什麼

- **資料**：沿用凍結的 synthetic-v2 與 v2.1 J 範圍（`data/synthetic-v2.1/scoring-scope.json`）。共 1,230 對資料，再加上 80 個 T10 文件集。
- **題目與 J arm 對齊**：
  - **single**：只給 new 段落，`choice` 題，用 `single_instructions` 加上 `labels_alt` 的四個選項。分數 = 1 − P(on_track)。
  - **paired**：輸入用 J 的 OLD/NEW 版面，`noul` 題，用 `paired_instructions`，true／false 描述沿用 `paired_options` 的 A／B。分數 = `noul`。
  - **docset**：T10 三段 new 串接後問 single 題。
- **API 差異**：Decisions API 沒有 system prompt，所以 J 的 SYSTEM 文字沒有帶入；選項鍵用 `on_track/delayed/blocked/cancelled`，不用 A–D。
- **AUROC 算法**：和 `src/report_v2.matched` 相同，都是同底稿的專屬負例、排除 T9。J 的數字由本 repo 既存分數重算，與 v2.1 summary 一致。

重跑指令（需要 `GEMINI_API_KEY`、`GOOGLE_API_KEY` 或 `gemini_key` 其中一個環境變數）：

```bash
.mpvenv/bin/python src/run_decision1.py --output results/gemini-decision-1-repeat
```

## 主表：專屬負例配對 AUROC

| 配對 | GD1 single | J-E2B single | J-E4B single | GD1 paired | J-E2B paired | J-E4B paired |
|---|---|---|---|---|---|---|
| T5-word | **0.999** | 0.689 | 0.939 | 0.872 | 1.000 | 0.768 |
| T6-word | **0.998** | 0.889 | 0.955 | 1.000 | 0.994 | 1.000 |
| T6-sentence | 1.000 | 0.998 | 1.000 | 1.000 | 1.000 | 1.000 |
| T7-word | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| T7-sentence | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| T8-sentence | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| T8-paragraph | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

T10 三段串接（40 正／40 負）的 AUROC：GD1 1.000、J-E2B 0.773、J-E4B 0.989。

## argmax 不等於排序

AUROC 只量排序。若直接看 single 題的 argmax：

- **負例**：T3、T4、T9 共 580 筆全部判成 on_track，**沒有誤報**。
- **T7、T8**：240 筆全部判成「非 on_track」。
- **T6**：只有 198/350 判成「非 on_track」（en 90/175、zh 108/175）。
- **T5**：只有 22/60 判成「非 on_track」（en 14/30、zh 8/30）。例如「預計 11-25、截止 11-20」只得到 P(on_track)=0.54、P(delayed)=0.42。

所以 T5 能排得好，但用 0.5 當門檻仍會漏掉一半以上。

## 成本與延遲

| 項目 | 數值 |
|---|---|
| 請求數 | 2,540 次，0 錯誤 |
| 端到端延遲（含網路，8 併發） | 平均 280 ms、p50 277 ms、p95 375 ms |
| 輸入 tokens | 648,092；按 $0.10/M 計約 **US$0.065**，無輸出費 |
| 對照：J（本機 CPU） | E2B 平均 7.2 s、E4B 平均 16.1 s |

雲端延遲與本機 CPU 不是同一台機器，只能當量級參考，**不符合 §11.4「同一台機器」的規定**。

## 限制

- 合成資料已經接近天花板，多數格子都是 1.000，不足以區分方法優劣。
- 託管模型隨時可能更新，結果無法固定重現。
- 資料會送到 Google 雲端，與 J 以及 MediaPipe Decision Maker 的本機、離線定位不同。
- MediaPipe Decision Maker（D2-DM）的 EG2、Laya、GLiNER 三個 backend 已另外跑完，見 [docs/decision-backends.md](../../docs/decision-backends.md)。

設計對照與三種 decision 後端的綜合解讀見 [docs/decision-backends.md](../../docs/decision-backends.md)。

原始輸出：`predictions.jsonl`（每次請求的機率、usage、延遲；不含金鑰）、`scores.jsonl`、`docset-scores.jsonl`、`summary.json`。

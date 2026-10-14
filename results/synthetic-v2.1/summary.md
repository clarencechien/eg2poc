# v0.2.1：jevlike J arm 合成試驗

依 `main@fb62b10` 的規格追加 J。資料、標籤與配對關係沿用已凍結的 synthetic-v2；沒有新增 Gemini 呼叫。

目前模型狀態：E2B=complete；E4B=running。未完成的品質指標不填零。

主表 AUROC 是同底稿專屬負例池的排序指標，不是逐對勝率或分類準確率；中英分層另列。

J 使用 `jevlike@9838918533cf3d88dc975ef19d38122b07df47f7` 的既有四選一／布林題介面，未改 prompt 模板。llama.cpp 固定 b11371（99b95488），CPU、4 threads、Q8_0。

## 主表：專屬負例配對 AUROC

| 配對 | C-alt class | D2-alt paired | D2-alt single | J-E2B single | J-E4B single | R |
|---|---|---|---|---|---|---|
| T5-word | 0.317 | 0.642 | 0.512 | 0.689 | — | 1.000 |
| T6-word | 0.997 | 0.998 | 0.922 | 0.889 | — | — |
| T6-sentence | 1.000 | 1.000 | 0.990 | 0.998 | — | — |
| T7-word | 0.999 | 1.000 | 0.966 | 1.000 | — | — |
| T7-sentence | 1.000 | 1.000 | 0.996 | 1.000 | — | — |
| T8-sentence | 1.000 | 0.985 | 0.951 | 1.000 | — | — |
| T8-paragraph | 0.999 | 0.959 | 1.000 | 1.000 | — | — |

J 缺選項記 null；有效樣本數、共同樣本比較與 H8–H11 見完整報告。T10 是未獨立覆核的合成政策任務，不能外推真實文件。

## 成本：同一台 CPU、同一批 100 筆

| arm | 平均端到端 ms | p95 ms | 平均 prefill ms | 平均輸入 tokens | 模型 | prewarm 後可否固定預算 |
|---|---|---|---|---|---|---|
| C_alt_classification | 240.918 | 305.978 | — | 72.610 | 271.0M / float32 | 標籤／old 已預算；new embedding 仍隨長度變動 |
| D2_alt_single | 435.707 | 605.077 | — | 287.520 | 278.8M / float32 | 4 組 premise/hypothesis，單批 forward；仍隨長度變動 |
| J_e2b | 7235.885 | 10330.065 | 7208.342 | 190.780 | 5.05 GB / Q8_0 | 每題一次 prefill；隨輸入長度變動 |
| J_e4b | 尚無完整測量 | — | — | — | — | — |

所有 arm 先做一次不計時 warmup，再逐段測量；J 的 100 筆成本測試關閉 prompt cache。這 100 筆預測沿用於品質評估，其餘品質推論啟用既有 prefix cache；兩者逐題標記，不能把品質推論的延遲混入成本表。D2 四個標籤以一批計算，token 數是四組總和；J 題目包含標籤與模板，token 數自然不同。EG2 的 old 向量與 label 已預算，時間包含 new embedding；僅有既有向量的投影運算可視為固定維度成本。

[完整結果、H8–H11、限制](report.md)

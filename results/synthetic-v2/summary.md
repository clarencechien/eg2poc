# v0.2 合成試驗摘要

在合成骨架內，完成 420 段底稿、1,690 組比較、40 對文件集；全部規則生成，沒有 Gemini 呼叫或獨立標註。

| 配對 | B768 | C_same_classification | C_alt_classification | C_xlang_classification | D1 | D2_same_paired | D2_same_single | R |
|---|---|---|---|---|---|---|---|---|
| T5-word | 0.879 | 0.243 | 0.317 | 0.487 | 0.536 | 0.509 | 0.509 | 1.000 |
| T6-word | 0.851 | 0.994 | 0.997 | 0.999 | 1.000 | 0.996 | 0.833 | — |
| T7-word | 0.942 | 0.999 | 0.999 | 1.000 | 1.000 | 1.000 | 0.873 | — |
| T8-sentence | 0.930 | 1.000 | 1.000 | 1.000 | 1.000 | 0.999 | 0.881 | — |
| T8-paragraph | 0.455 | 1.000 | 0.999 | 1.000 | 0.725 | 0.999 | 1.000 | — |

H1（兩種前綴、T6/T7 word）數值條件：4/4 通過；H2：3/4 通過。
H3：{"same": true, "alt": true, "xlang": true}；H4：{"same": true, "alt": true, "xlang": true}；H5：True。

H6 只有合成政策任務結果；H7 的 C-xlang/SearchQuery 在 T8 paragraph 跨骨架 AUROC 範圍為 0.125（門檻 <0.10），且缺少 LLM 改寫對照。所有推論僅限本批模板；T8 主表排除不確定的 T9，完整報告另有含 T9 的敏感度表。

配對 D2 的高 AUROC 不等於單邊偵測已經成立；即使 single 在本資料高分，也未測「原本就處於風險但本次未變」等必要反例。

[完整報告](report.md) · [配對與分層數值](metrics.json) · [圖](fig/paired-auroc.png) · [v1 日期重分析](v1-date-reanalysis.json)

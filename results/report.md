# EG2 實驗結果

v0.2 已完成 420 段底稿、1,690 組比較及 40 對正／負文件集。全部是規則模板合成資料，沒有 Gemini 呼叫或獨立覆核。
v0.2.1 的 J E2B／E4B 均已完成；兩者使用 jevlike 的原有判讀介面，各有 2,540 次有效預測，缺值皆為 0。

- [v0.2 摘要](synthetic-v2/summary.md)、[完整 Q1–Q7／H1–H7 報告](synthetic-v2/report.md)、[資料設計覆核](synthetic-v2/data-audit.md)。
- [v0.2.1 摘要](synthetic-v2.1/summary.md)、[完整報告](synthetic-v2.1/report.md)、[模型與執行紀錄](synthetic-v2.1/)。
- [CPU 硬體與效能 baseline](synthetic-v2.1/hardware-baseline.md)：Xeon Platinum 8573C、等效 4 CPU 配額、32 GiB RAM、4 threads、無 GPU 推論。
- [v0.1 歷史結果](synthetic-v1/summary.md)；[v1 日期對照重新分析](synthetic-v2/v1-date-reanalysis.json)。

在這批合成骨架內，C 的跨語言標籤未使 T6/T7 word 的 AUROC 明顯退步。
D2-alt single 在 T6 word／T7 word／T8 sentence 的 AUROC 分別為 0.922／0.966／0.951；
日期 T5/T4 只有 0.512，R 為 1.000。
T10 的 D2-alt single 三段取最大值為 0.545；T10 採人工定義的三信號政策，僅能探索。

J E2B single 在 H8 四個對照皆達 0.85，與 D2-alt single 的 AUROC 差距皆小於 0.05；
同機 100 筆平均耗時 7.24 秒，D2 為 0.436 秒。日期 T5 single 為 0.6886，paired 為 1.000；
T10 concat 為 0.7725，未達 H11 的 0.80。H9 以 single 判斷，因此仍未通過。

J E4B 的 T5 single 為 0.9386，T10 concat 為 0.9894，H9／探索性 H11 均達門檻；
但 T5 paired 為 0.7678，低於 E2B 的 1.000，不能說較大模型在所有題型都更好。
E4B 的 H8 達門檻，H10 四項與 D2-alt single 的差距也均小於 0.05；
同機平均每筆 16.08 秒，約為 E2B 的 2.22 倍、D2 的 36.9 倍。

v0.1 的日期合併負例結果不能支持跨截止日推理：改用 T5/T4 對照，NLI AUROC 為 0.485。
v1 的負例改一字，正例改三至四字，A/B/C 的高分亦受到編輯幅度混淆。原始分數與凍結資料均保留。

AUROC 是排序指標，不是四分類準確率。C 分布距離高分不代表 argmax 已變；
single 高分也未涵蓋「原本有風險但本次未變」的必要反例。
[重跑方式](../README.md)與各結果目錄的 manifest 保存版本、雜湊及執行狀態。

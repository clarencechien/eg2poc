# EG2 狀態漂移實驗報表

**規則模板合成底稿試驗：可觀察本資料上的表現，不能外推真實文件或排除生成器指紋。**

執行狀態：completed。樣本數：770。

D_NLI 表示 NLI 替代，並非 Decision Maker。E 僅在抽樣子集計分；各格括號為正例／負例數，不可直接與全量結果排序。
T9 不納入 AUROC；固定負例為 T1+T2+T3+T4。缺少一個 class 不計算 AUROC。

## 覆蓋缺口

- Some bases lack real repository provenance
- T5 rule/llm not balanced: [60, 0]
- T6 rule/llm not balanced: [150, 0]
- T7 rule/llm not balanced: [60, 0]

## AUROC：all

| 類別 | A | B768 | B256 | B2 | C_classification | C_search_query | D_NLI | E |
|---|---|---|---|---|---|---|---|---|
| T5 | 0.333 (60/270) | 0.426 (60/270) | 0.413 (60/270) | 未跑／樣本不足 | 0.645 (60/270) | 0.502 (60/270) | 0.885 (60/270) | 未跑／樣本不足 |
| T6 | 0.637 (150/270) | 0.584 (150/270) | 0.583 (150/270) | 未跑／樣本不足 | 0.909 (150/270) | 0.881 (150/270) | 0.979 (150/270) | 未跑／樣本不足 |
| T6-zh-沒有 | 0.606 (15/270) | 0.596 (15/270) | 0.589 (15/270) | 未跑／樣本不足 | 0.979 (15/270) | 0.970 (15/270) | 0.975 (15/270) | 未跑／樣本不足 |
| T6-zh-不再 | 0.640 (15/270) | 0.585 (15/270) | 0.587 (15/270) | 未跑／樣本不足 | 0.878 (15/270) | 0.789 (15/270) | 0.943 (15/270) | 未跑／樣本不足 |
| T6-zh-尚未 | 0.641 (15/270) | 0.560 (15/270) | 0.564 (15/270) | 未跑／樣本不足 | 0.857 (15/270) | 0.766 (15/270) | 0.979 (15/270) | 未跑／樣本不足 |
| T6-zh-取消 | 0.608 (15/270) | 0.578 (15/270) | 0.574 (15/270) | 未跑／樣本不足 | 0.991 (15/270) | 0.996 (15/270) | 0.964 (15/270) | 未跑／樣本不足 |
| T6-zh-暫停 | 0.608 (15/270) | 0.573 (15/270) | 0.564 (15/270) | 未跑／樣本不足 | 0.941 (15/270) | 0.956 (15/270) | 0.956 (15/270) | 未跑／樣本不足 |
| T6-en | 0.653 (75/270) | 0.590 (75/270) | 0.591 (75/270) | 未跑／樣本不足 | 0.889 (75/270) | 0.867 (75/270) | 0.994 (75/270) | 未跑／樣本不足 |
| T7 | 0.505 (60/270) | 0.461 (60/270) | 0.471 (60/270) | 未跑／樣本不足 | 0.890 (60/270) | 0.954 (60/270) | 0.940 (60/270) | 未跑／樣本不足 |
| T8 | 0.672 (90/270) | 0.714 (90/270) | 0.714 (90/270) | 未跑／樣本不足 | 0.988 (90/270) | 0.972 (90/270) | 0.521 (90/270) | 未跑／樣本不足 |

## AUROC：rule

| 類別 | A | B768 | B256 | B2 | C_classification | C_search_query | D_NLI | E |
|---|---|---|---|---|---|---|---|---|
| T5 | 0.333 (60/270) | 0.426 (60/270) | 0.413 (60/270) | 未跑／樣本不足 | 0.645 (60/270) | 0.502 (60/270) | 0.885 (60/270) | 未跑／樣本不足 |
| T6 | 0.637 (150/270) | 0.584 (150/270) | 0.583 (150/270) | 未跑／樣本不足 | 0.909 (150/270) | 0.881 (150/270) | 0.979 (150/270) | 未跑／樣本不足 |
| T6-zh-沒有 | 0.606 (15/270) | 0.596 (15/270) | 0.589 (15/270) | 未跑／樣本不足 | 0.979 (15/270) | 0.970 (15/270) | 0.975 (15/270) | 未跑／樣本不足 |
| T6-zh-不再 | 0.640 (15/270) | 0.585 (15/270) | 0.587 (15/270) | 未跑／樣本不足 | 0.878 (15/270) | 0.789 (15/270) | 0.943 (15/270) | 未跑／樣本不足 |
| T6-zh-尚未 | 0.641 (15/270) | 0.560 (15/270) | 0.564 (15/270) | 未跑／樣本不足 | 0.857 (15/270) | 0.766 (15/270) | 0.979 (15/270) | 未跑／樣本不足 |
| T6-zh-取消 | 0.608 (15/270) | 0.578 (15/270) | 0.574 (15/270) | 未跑／樣本不足 | 0.991 (15/270) | 0.996 (15/270) | 0.964 (15/270) | 未跑／樣本不足 |
| T6-zh-暫停 | 0.608 (15/270) | 0.573 (15/270) | 0.564 (15/270) | 未跑／樣本不足 | 0.941 (15/270) | 0.956 (15/270) | 0.956 (15/270) | 未跑／樣本不足 |
| T6-en | 0.653 (75/270) | 0.590 (75/270) | 0.591 (75/270) | 未跑／樣本不足 | 0.889 (75/270) | 0.867 (75/270) | 0.994 (75/270) | 未跑／樣本不足 |
| T7 | 0.505 (60/270) | 0.461 (60/270) | 0.471 (60/270) | 未跑／樣本不足 | 0.890 (60/270) | 0.954 (60/270) | 0.940 (60/270) | 未跑／樣本不足 |
| T8 | 0.672 (90/270) | 0.714 (90/270) | 0.714 (90/270) | 未跑／樣本不足 | 0.988 (90/270) | 0.972 (90/270) | 0.521 (90/270) | 未跑／樣本不足 |

## AUROC：llm

| 類別 | A | B768 | B256 | B2 | C_classification | C_search_query | D_NLI | E |
|---|---|---|---|---|---|---|---|---|
| T5 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-沒有 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-不再 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-尚未 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-取消 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-zh-暫停 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T6-en | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T7 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |
| T8 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 | 未跑／樣本不足 |

## Q6 雜訊底線

| run | batch | n | mean | std | p95 | max |
|---|---|---|---|---|---|---|
| 1 | 1 | 100 | 3.69494435048523e-13 | 2.2249365900072964e-13 | 6.500688876087679e-13 | 1.7932322293745528e-12 |
| 2 | 8 | 100 | 4.5519144009631415e-17 | 8.755289445502247e-17 | 2.220446049250313e-16 | 2.220446049250313e-16 |
| 3 | 32 | 100 | 4.5643488988389436e-14 | 1.0583162682532916e-13 | 2.949307464916728e-13 | 3.9013237085328e-13 |

## Q7 靈敏度

| 類別 | strength | n | B mean | B p50 | 超過 noise p95 比例 |
|---|---|---|---|---|---|
| T3 | word | 30 | 0.0029891370464342646 | 0.001542932994824442 | 1.0 |
| T3 | sentence | 30 | 0.005120299626633 | 0.00455248589781998 | 1.0 |
| T3 | paragraph | 30 | 0.0285632261616127 | 0.02939520426152914 | 1.0 |
| T6 | word | 50 | 0.004579796283883457 | 0.0035781163181849984 | 1.0 |
| T6 | sentence | 50 | 0.009773717096664778 | 0.008450028659093445 | 1.0 |
| T6 | paragraph | 50 | 0.03510379616515927 | 0.03462689662218993 | 1.0 |
| T8 | word | 30 | 0.008384530719152846 | 0.008363385788034028 | 1.0 |
| T8 | sentence | 30 | 0.025619608408785098 | 0.024782833629402423 | 1.0 |
| T8 | paragraph | 30 | 0.05365489654593452 | 0.0554465994143693 | 1.0 |

## 每類／arm 最極端樣本（最多 5 筆；需人工覆核）

### T1 / A

- `syn-zh-007:T1:rule:71` score=0.051546
  - old: "備份還原第8輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  備份還原第8輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-069:T1:rule:50` score=0.051020
  - old: "訂單追蹤第70輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  訂單追蹤第70輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-061:T1:rule:54` score=0.051020
  - old: "庫存同步第62輪交付由家豪負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  庫存同步第62輪交付由家豪負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-065:T1:rule:56` score=0.051020
  - old: "通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-067:T1:rule:61` score=0.051020
  - old: "備份還原第68輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  備份還原第68輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
### T1 / B768

- `syn-zh-065:T1:rule:56` score=0.039935
  - old: "通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-074:T1:rule:68` score=0.039542
  - old: "客服工作台第75輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  客服工作台第75輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-050:T1:rule:77` score=0.038747
  - old: "通知佇列第51輪交付由怡君負責。團隊已暫停本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  通知佇列第51輪交付由怡君負責。團隊已暫停本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-080:T1:rule:62` score=0.038636
  - old: "通知佇列第81輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  通知佇列第81輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-075:T1:rule:55` score=0.037814
  - old: "付款服務第76輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  付款服務第76輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
### T1 / B256

- `syn-zh-074:T1:rule:68` score=0.037758
  - old: "客服工作台第75輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  客服工作台第75輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-030:T1:rule:70` score=0.036205
  - old: "付款服務第31輪交付由怡君負責。目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  付款服務第31輪交付由怡君負責。目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-075:T1:rule:55` score=0.035371
  - old: "付款服務第76輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  付款服務第76輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-065:T1:rule:56` score=0.034223
  - old: "通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-050:T1:rule:77` score=0.033446
  - old: "通知佇列第51輪交付由怡君負責。團隊已暫停本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  通知佇列第51輪交付由怡君負責。團隊已暫停本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
### T1 / C_classification

- `syn-en-038:T1:rule:461` score=0.018772
  - old: "Cycle 39 of access control is owned by Casey. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 39 of access control is owned by Casey. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
- `syn-en-059:T1:rule:457` score=0.011661
  - old: "Cycle 60 of support console is owned by Taylor. The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 60 of support console is owned by Taylor. The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
- `syn-en-046:T1:rule:444` score=0.006900
  - old: "Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
- `syn-en-058:T1:rule:453` score=0.006104
  - old: "Cycle 59 of document portal is owned by Casey. The team has paused deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 59 of document portal is owned by Casey. The team has paused deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
- `syn-en-016:T1:rule:462` score=0.004109
  - old: "Cycle 17 of stock sync is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 17 of stock sync is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
### T1 / C_search_query

- `syn-en-038:T1:rule:461` score=0.015379
  - old: "Cycle 39 of access control is owned by Casey. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 39 of access control is owned by Casey. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
- `syn-en-059:T1:rule:457` score=0.012030
  - old: "Cycle 60 of support console is owned by Taylor. The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 60 of support console is owned by Taylor. The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
- `syn-en-046:T1:rule:444` score=0.007164
  - old: "Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "  Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover recrods at the team meeting.\n"
- `syn-zh-040:T1:rule:60` score=0.006481
  - old: "監控平台第41輪交付由怡君負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  監控平台第41輪交付由怡君負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-055:T1:rule:65` score=0.005097
  - old: "監控平台第56輪交付由怡君負責。團隊已暫停本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  監控平台第56輪交付由怡君負責。團隊已暫停本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
### T1 / D_NLI

- `syn-zh-079:T1:rule:73` score=0.230138
  - old: "資料搬遷第80輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  資料搬遷第80輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-086:T1:rule:52` score=0.214597
  - old: "稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-089:T1:rule:64` score=0.200292
  - old: "客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-081:T1:rule:58` score=0.190925
  - old: "搜尋索引第82輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  搜尋索引第82輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
- `syn-zh-080:T1:rule:62` score=0.189463
  - old: "通知佇列第81輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "  通知佇列第81輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次記錄包含測試結果、相依項目清單及交接文仵，指定負責人會在例會中確認相關細節。\n"
### T2 / A

- `syn-en-051:T2:rule:466` score=0.393443
  - old: "Cycle 52 of search indexing is owned by Morgan. The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 52 of search indexing is owned by Morgan."
- `syn-en-052:T2:rule:479` score=0.393443
  - old: "Cycle 53 of backup recovery is owned by Jordan. The team has paused deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has paused deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 53 of backup recovery is owned by Jordan."
- `syn-en-037:T2:rule:475` score=0.388664
  - old: "Cycle 38 of backup recovery is owned by Jordan. The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 38 of backup recovery is owned by Jordan."
- `syn-en-044:T2:rule:494` score=0.388664
  - old: "Cycle 45 of support console is owned by Taylor. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 45 of support console is owned by Taylor."
- `syn-en-049:T2:rule:465` score=0.386831
  - old: "Cycle 50 of data migration is owned by Taylor. The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has paused deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 50 of data migration is owned by Taylor."
### T2 / B768

- `syn-zh-009:T2:rule:101` score=0.033527
  - old: "訂單追蹤第10輪交付由品妤負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。訂單追蹤第10輪交付由品妤負責。"
- `syn-zh-013:T2:rule:86` score=0.032568
  - old: "文件入口第14輪交付由柏宇負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。文件入口第14輪交付由柏宇負責。"
- `syn-zh-036:T2:rule:81` score=0.030956
  - old: "搜尋索引第37輪交付由家豪負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。搜尋索引第37輪交付由家豪負責。"
- `syn-zh-073:T2:rule:106` score=0.030510
  - old: "文件入口第74輪交付由柏宇負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。文件入口第74輪交付由柏宇負責。"
- `syn-zh-024:T2:rule:88` score=0.030169
  - old: "訂單追蹤第25輪交付由品妤負責。目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。訂單追蹤第25輪交付由品妤負責。"
### T2 / B256

- `syn-zh-009:T2:rule:101` score=0.030829
  - old: "訂單追蹤第10輪交付由品妤負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。訂單追蹤第10輪交付由品妤負責。"
- `syn-zh-013:T2:rule:86` score=0.030378
  - old: "文件入口第14輪交付由柏宇負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。文件入口第14輪交付由柏宇負責。"
- `syn-zh-036:T2:rule:81` score=0.028830
  - old: "搜尋索引第37輪交付由家豪負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。搜尋索引第37輪交付由家豪負責。"
- `syn-zh-073:T2:rule:106` score=0.028557
  - old: "文件入口第74輪交付由柏宇負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。文件入口第74輪交付由柏宇負責。"
- `syn-zh-024:T2:rule:88` score=0.027837
  - old: "訂單追蹤第25輪交付由品妤負責。目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。訂單追蹤第25輪交付由品妤負責。"
### T2 / C_classification

- `syn-en-047:T2:rule:487` score=0.050879
  - old: "Cycle 48 of authentication is owned by Jordan. The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 48 of authentication is owned by Jordan."
- `syn-zh-046:T2:rule:91` score=0.021810
  - old: "庫存同步第47輪交付由家豪負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。庫存同步第47輪交付由家豪負責。"
- `syn-en-037:T2:rule:475` score=0.016308
  - old: "Cycle 38 of backup recovery is owned by Jordan. The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 38 of backup recovery is owned by Jordan."
- `syn-en-041:T2:rule:490` score=0.014052
  - old: "Cycle 42 of audit logging is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 42 of audit logging is owned by Morgan."
- `syn-zh-047:T2:rule:104` score=0.013394
  - old: "身分驗證第48輪交付由雅婷負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。身分驗證第48輪交付由雅婷負責。"
### T2 / C_search_query

- `syn-en-047:T2:rule:487` score=0.042793
  - old: "Cycle 48 of authentication is owned by Jordan. The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 48 of authentication is owned by Jordan."
- `syn-zh-046:T2:rule:91` score=0.027567
  - old: "庫存同步第47輪交付由家豪負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。庫存同步第47輪交付由家豪負責。"
- `syn-zh-047:T2:rule:104` score=0.020828
  - old: "身分驗證第48輪交付由雅婷負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。身分驗證第48輪交付由雅婷負責。"
- `syn-en-039:T2:rule:484` score=0.015947
  - old: "Cycle 40 of order tracking is owned by Taylor. The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "The team has cancelled deployment. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting. Cycle 40 of order tracking is owned by Taylor."
- `syn-zh-044:T2:rule:84` score=0.014851
  - old: "客服工作台第45輪交付由品妤負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。客服工作台第45輪交付由品妤負責。"
### T2 / D_NLI

- `syn-zh-025:T2:rule:95` score=0.117407
  - old: "監控平台第26輪交付由怡君負責。目前資料核對尚未完成。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前資料核對尚未完成。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。監控平台第26輪交付由怡君負責。"
- `syn-zh-027:T2:rule:80` score=0.100824
  - old: "帳務核對第28輪交付由雅婷負責。目前資料核對尚未完成。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前資料核對尚未完成。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。帳務核對第28輪交付由雅婷負責。"
- `syn-zh-024:T2:rule:88` score=0.092580
  - old: "訂單追蹤第25輪交付由品妤負責。目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。訂單追蹤第25輪交付由品妤負責。"
- `syn-zh-035:T2:rule:107` score=0.065819
  - old: "通知佇列第36輪交付由怡君負責。目前資料核對尚未完成。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "目前資料核對尚未完成。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。通知佇列第36輪交付由怡君負責。"
- `syn-zh-052:T2:rule:96` score=0.064155
  - old: "備份還原第53輪交付由雅婷負責。團隊已暫停本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "團隊已暫停本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。備份還原第53輪交付由雅婷負責。"
### T3 / A

- `syn-zh-069:T3:rule:112` score=0.438776
  - old: "訂單追蹤第70輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "品妤負責訂單追蹤第70輪的交付工作。目前進度領先計畫。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-061:T3:rule:124` score=0.438776
  - old: "庫存同步第62輪交付由家豪負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "家豪負責庫存同步第62輪的交付工作。目前進度領先計畫。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-065:T3:rule:130` score=0.438776
  - old: "通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "怡君負責通知佇列第66輪的交付工作。目前進度領先計畫。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-067:T3:rule:145` score=0.438776
  - old: "備份還原第68輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責備份還原第68輪的交付工作。目前進度領先計畫。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-042:T3:rule:133` score=0.434343
  - old: "帳務核對第43輪交付由雅婷負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責帳務核對第43輪的交付工作。團隊已取消本輪部署。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
### T3 / B768

- `syn-zh-089:T3:rule:154` score=0.037248
  - old: "客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "品妤負責客服工作台第90輪的交付工作。文件記錄本輪交付的工作安排。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-022:T3:rule:115` score=0.036399
  - old: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責備份還原第23輪的交付工作。權限問題不再阻礙驗收。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-045:T3:rule:139` score=0.034596
  - old: "付款服務第46輪交付由怡君負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "怡君負責付款服務第46輪的交付工作。團隊已取消本輪部署。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-042:T3:rule:133` score=0.033491
  - old: "帳務核對第43輪交付由雅婷負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責帳務核對第43輪的交付工作。團隊已取消本輪部署。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-075:T3:rule:127` score=0.033298
  - old: "付款服務第76輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "怡君負責付款服務第76輪的交付工作。文件記錄本輪交付的工作安排。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
### T3 / B256

- `syn-zh-075:T3:rule:127` score=0.034772
  - old: "付款服務第76輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "怡君負責付款服務第76輪的交付工作。文件記錄本輪交付的工作安排。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-045:T3:rule:139` score=0.034640
  - old: "付款服務第46輪交付由怡君負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "怡君負責付款服務第46輪的交付工作。團隊已取消本輪部署。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-022:T3:rule:115` score=0.034510
  - old: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責備份還原第23輪的交付工作。權限問題不再阻礙驗收。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-042:T3:rule:133` score=0.034487
  - old: "帳務核對第43輪交付由雅婷負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責帳務核對第43輪的交付工作。團隊已取消本輪部署。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-067:T3:rule:145` score=0.032637
  - old: "備份還原第68輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責備份還原第68輪的交付工作。目前進度領先計畫。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
### T3 / C_classification

- `syn-en-068:T3:rule:527` score=0.006718
  - old: "Cycle 69 of access control is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Casey owns cycle 69 of the access control delivery. Progress is currently ahead of schedule. Delivery is planned for 2026-11-10 against a deadline of 2026-11-28. The named owner will review test results, dependency lists, and handover records at the team meeting."
- `syn-zh-019:T3:rule:121` score=0.006398
  - old: "資料搬遷第20輪交付由品妤負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "品妤負責資料搬遷第20輪的交付工作。權限問題不再阻礙驗收。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-en-012:T3:rule:503` score=0.006363
  - old: "Cycle 13 of billing checks is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Jordan owns cycle 13 of the billing checks delivery. The access issue no longer blocks review. Delivery is planned for 2026-11-10 against a deadline of 2026-11-28. The named owner will review test results, dependency lists, and handover records at the team meeting."
- `syn-en-046:T3:rule:523` score=0.004707
  - old: "Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The assigned owner will review test results, dependency lists, and handover records at the team meeting."
- `syn-zh-089:T3:rule:154` score=0.004276
  - old: "客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "品妤負責客服工作台第90輪的交付工作。文件記錄本輪交付的工作安排。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
### T3 / C_search_query

- `syn-zh-019:T3:rule:121` score=0.009826
  - old: "資料搬遷第20輪交付由品妤負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "品妤負責資料搬遷第20輪的交付工作。權限問題不再阻礙驗收。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-089:T3:rule:154` score=0.007622
  - old: "客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "品妤負責客服工作台第90輪的交付工作。文件記錄本輪交付的工作安排。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-042:T3:rule:133` score=0.006232
  - old: "帳務核對第43輪交付由雅婷負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責帳務核對第43輪的交付工作。團隊已取消本輪部署。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-en-046:T3:rule:523` score=0.005868
  - old: "Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 47 of stock sync is owned by Morgan. The team has cancelled deployment. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The assigned owner will review test results, dependency lists, and handover records at the team meeting."
- `syn-en-012:T3:rule:503` score=0.005530
  - old: "Cycle 13 of billing checks is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Jordan owns cycle 13 of the billing checks delivery. The access issue no longer blocks review. Delivery is planned for 2026-11-10 against a deadline of 2026-11-28. The named owner will review test results, dependency lists, and handover records at the team meeting."
### T3 / D_NLI

- `syn-en-012:T3:rule:501` score=0.184752
  - old: "Cycle 13 of billing checks is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 13 of billing reviews is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-018:T3:rule:500` score=0.118153
  - old: "Cycle 19 of report export is owned by Casey. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Casey owns cycle 19 of the report export delivery. The access issue no longer blocks review. Delivery is planned for 2026-11-10 against a deadline of 2026-11-28. The named owner will review test results, dependency lists, and handover records at the team meeting."
- `syn-zh-067:T3:rule:143` score=0.107371
  - old: "備份還原第68輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "備份還原第68輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄涵蓋測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-045:T3:rule:137` score=0.105835
  - old: "付款服務第46輪交付由怡君負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第46輪交付由怡君負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄涵蓋測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-022:T3:rule:113` score=0.103733
  - old: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄涵蓋測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T4 / A

- `syn-zh-000:T4:rule:155` score=0.010309
  - old: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-001:T4:rule:157` score=0.010309
  - old: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-002:T4:rule:159` score=0.010309
  - old: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-003:T4:rule:161` score=0.010309
  - old: "報表匯出第4輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "報表匯出第4輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-004:T4:rule:163` score=0.010309
  - old: "資料搬遷第5輪交付由品妤負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第5輪交付由品妤負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T4 / B768

- `syn-zh-000:T4:rule:155` score=0.003068
  - old: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-001:T4:rule:157` score=0.002669
  - old: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-005:T4:rule:165` score=0.002397
  - old: "通知佇列第6輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "通知佇列第6輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-002:T4:rule:159` score=0.002223
  - old: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-015:T4:rule:185` score=0.002218
  - old: "付款服務第16輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第16輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T4 / B256

- `syn-zh-000:T4:rule:155` score=0.002827
  - old: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-001:T4:rule:157` score=0.002380
  - old: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-005:T4:rule:165` score=0.002126
  - old: "通知佇列第6輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "通知佇列第6輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-002:T4:rule:159` score=0.002096
  - old: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-015:T4:rule:185` score=0.002001
  - old: "付款服務第16輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第16輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-12-20，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T4 / C_classification

- `syn-zh-000:T4:rule:155` score=0.000301
  - old: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-022:T4:rule:199` score=0.000281
  - old: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-014:T4:rule:183` score=0.000267
  - old: "客服工作台第15輪交付由品妤負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "客服工作台第15輪交付由品妤負責。權限問題不再阻礙驗收。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-008:T4:rule:171` score=0.000258
  - old: "權限管理第9輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "權限管理第9輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-006:T4:rule:167` score=0.000257
  - old: "搜尋索引第7輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "搜尋索引第7輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T4 / C_search_query

- `syn-zh-008:T4:rule:171` score=0.000287
  - old: "權限管理第9輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "權限管理第9輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-022:T4:rule:199` score=0.000220
  - old: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "備份還原第23輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-000:T4:rule:155` score=0.000217
  - old: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第1輪交付由怡君負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-020:T4:rule:195` score=0.000209
  - old: "通知佇列第21輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "通知佇列第21輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-002:T4:rule:159` score=0.000198
  - old: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-20，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T4 / D_NLI

- `syn-en-076:T4:rule:590` score=0.999209
  - old: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-20; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-080:T4:rule:598` score=0.999102
  - old: "Cycle 81 of notifications is owned by Alex. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 81 of notifications is owned by Alex. This document records the delivery arrangements. The planned delivery is 2026-11-20; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-078:T4:rule:594` score=0.998981
  - old: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-20; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-006:T4:rule:552` score=0.998936
  - old: "Cycle 7 of search indexing is owned by Morgan. The review currently has no blockers. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 7 of search indexing is owned by Morgan. The review currently has no blockers. The planned delivery is 2026-11-20; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-000:T4:rule:540` score=0.998800
  - old: "Cycle 1 of payments is owned by Alex. The review currently has no blockers. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 1 of payments is owned by Alex. The review currently has no blockers. The planned delivery is 2026-11-20; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T5 / A

- `syn-en-078:T5:rule:595` score=0.011628
  - old: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-080:T5:rule:599` score=0.011673
  - old: "Cycle 81 of notifications is owned by Alex. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 81 of notifications is owned by Alex. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-076:T5:rule:591` score=0.011719
  - old: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-014:T5:rule:569` score=0.011811
  - old: "Cycle 15 of support console is owned by Taylor. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 15 of support console is owned by Taylor. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-022:T5:rule:585` score=0.011811
  - old: "Cycle 23 of backup recovery is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 23 of backup recovery is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T5 / B768

- `syn-en-078:T5:rule:595` score=0.005435
  - old: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-076:T5:rule:591` score=0.005467
  - old: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-016:T5:rule:573` score=0.005543
  - old: "Cycle 17 of stock sync is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 17 of stock sync is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-021:T5:rule:583` score=0.005991
  - old: "Cycle 22 of search indexing is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 22 of search indexing is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-022:T5:rule:585` score=0.006190
  - old: "Cycle 23 of backup recovery is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 23 of backup recovery is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T5 / B256

- `syn-en-016:T5:rule:573` score=0.004865
  - old: "Cycle 17 of stock sync is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 17 of stock sync is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-076:T5:rule:591` score=0.004938
  - old: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-021:T5:rule:583` score=0.004942
  - old: "Cycle 22 of search indexing is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 22 of search indexing is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-078:T5:rule:595` score=0.004973
  - old: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-022:T5:rule:585` score=0.005266
  - old: "Cycle 23 of backup recovery is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 23 of backup recovery is owned by Jordan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T5 / C_classification

- `syn-en-078:T5:rule:595` score=0.000254
  - old: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 79 of report export is owned by Casey. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-080:T5:rule:599` score=0.000263
  - old: "Cycle 81 of notifications is owned by Alex. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 81 of notifications is owned by Alex. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-075:T5:rule:589` score=0.000299
  - old: "Cycle 76 of payments is owned by Alex. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 76 of payments is owned by Alex. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-076:T5:rule:591` score=0.000305
  - old: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-zh-076:T5:rule:206` score=0.000323
  - old: "庫存同步第77輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第77輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2027-01-30，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T5 / C_search_query

- `syn-en-075:T5:rule:589` score=0.000153
  - old: "Cycle 76 of payments is owned by Alex. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 76 of payments is owned by Alex. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-076:T5:rule:591` score=0.000162
  - old: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-018:T5:rule:577` score=0.000196
  - old: "Cycle 19 of report export is owned by Casey. The access issue no longer blocks review. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 19 of report export is owned by Casey. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-015:T5:rule:571` score=0.000205
  - old: "Cycle 16 of payments is owned by Alex. The access issue no longer blocks review. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 16 of payments is owned by Alex. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-021:T5:rule:583` score=0.000217
  - old: "Cycle 22 of search indexing is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 22 of search indexing is owned by Morgan. The access issue no longer blocks review. The planned delivery is 2027-01-30; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T5 / D_NLI

- `syn-zh-023:T5:rule:202` score=0.940637
  - old: "權限管理第24輪交付由柏宇負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "權限管理第24輪交付由柏宇負責。權限問題不再阻礙驗收。預計交付日為2027-01-30，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-021:T5:rule:198` score=0.941757
  - old: "搜尋索引第22輪交付由家豪負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "搜尋索引第22輪交付由家豪負責。權限問題不再阻礙驗收。預計交付日為2027-01-30，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-003:T5:rule:162` score=0.962198
  - old: "報表匯出第4輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "報表匯出第4輪交付由柏宇負責。目前驗收沒有阻礙。預計交付日為2027-01-30，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-001:T5:rule:158` score=0.965476
  - old: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第2輪交付由家豪負責。目前驗收沒有阻礙。預計交付日為2027-01-30，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-015:T5:rule:186` score=0.974124
  - old: "付款服務第16輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第16輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2027-01-30，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T6 / A

- `syn-zh-036:T6:rule:260` score=0.010101
  - old: "搜尋索引第37輪交付由家豪負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "搜尋索引第37輪交付由家豪負責。團隊未取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-037:T6:rule:263` score=0.010101
  - old: "備份還原第38輪交付由雅婷負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "備份還原第38輪交付由雅婷負責。團隊未取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-038:T6:rule:266` score=0.010101
  - old: "權限管理第39輪交付由柏宇負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "權限管理第39輪交付由柏宇負責。團隊未取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-039:T6:rule:269` score=0.010101
  - old: "訂單追蹤第40輪交付由品妤負責。團隊已取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "訂單追蹤第40輪交付由品妤負責。團隊未取消本輪部署。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-040:T6:rule:272` score=0.010101
  - old: "監控平台第41輪交付由怡君負責。團隊已取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "監控平台第41輪交付由怡君負責。團隊未取消本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T6 / B768

- `syn-en-024:T6:rule:630` score=0.001815
  - old: "Cycle 25 of order tracking is owned by Taylor. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 25 of order tracking is owned by Taylor. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-027:T6:rule:639` score=0.001828
  - old: "Cycle 28 of billing checks is owned by Jordan. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 28 of billing checks is owned by Jordan. Data verification is already complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-026:T6:rule:636` score=0.001848
  - old: "Cycle 27 of audit logging is owned by Morgan. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 27 of audit logging is owned by Morgan. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-zh-004:T6:rule:227` score=0.001928
  - old: "資料搬遷第5輪交付由品妤負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第5輪交付由品妤負責。目前驗收有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-002:T6:rule:221` score=0.002109
  - old: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第3輪交付由雅婷負責。目前驗收有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T6 / B256

- `syn-en-026:T6:rule:636` score=0.001572
  - old: "Cycle 27 of audit logging is owned by Morgan. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 27 of audit logging is owned by Morgan. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-024:T6:rule:630` score=0.001602
  - old: "Cycle 25 of order tracking is owned by Taylor. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 25 of order tracking is owned by Taylor. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-zh-004:T6:rule:227` score=0.001620
  - old: "資料搬遷第5輪交付由品妤負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第5輪交付由品妤負責。目前驗收有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-en-027:T6:rule:639` score=0.001638
  - old: "Cycle 28 of billing checks is owned by Jordan. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 28 of billing checks is owned by Jordan. Data verification is already complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-zh-002:T6:rule:221` score=0.001821
  - old: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第3輪交付由雅婷負責。目前驗收有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T6 / C_classification

- `syn-en-024:T6:rule:630` score=0.000019
  - old: "Cycle 25 of order tracking is owned by Taylor. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 25 of order tracking is owned by Taylor. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-027:T6:rule:639` score=0.000051
  - old: "Cycle 28 of billing checks is owned by Jordan. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 28 of billing checks is owned by Jordan. Data verification is already complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-026:T6:rule:638` score=0.000084
  - old: "Cycle 27 of audit logging is owned by Morgan. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Morgan owns cycle 27 of the audit logging delivery. The team has now completed data verification. Delivery is planned for 2026-11-10 against a deadline of 2026-11-28. The named owner will review test results, dependency lists, and handover records at the team meeting."
- `syn-en-025:T6:rule:633` score=0.000129
  - old: "Cycle 26 of monitoring is owned by Alex. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 26 of monitoring is owned by Alex. Data verification is already complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-026:T6:rule:636` score=0.000131
  - old: "Cycle 27 of audit logging is owned by Morgan. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 27 of audit logging is owned by Morgan. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T6 / C_search_query

- `syn-en-025:T6:rule:633` score=0.000051
  - old: "Cycle 26 of monitoring is owned by Alex. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 26 of monitoring is owned by Alex. Data verification is already complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-026:T6:rule:636` score=0.000071
  - old: "Cycle 27 of audit logging is owned by Morgan. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 27 of audit logging is owned by Morgan. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-027:T6:rule:639` score=0.000115
  - old: "Cycle 28 of billing checks is owned by Jordan. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 28 of billing checks is owned by Jordan. Data verification is already complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-028:T6:rule:642` score=0.000123
  - old: "Cycle 29 of document portal is owned by Casey. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 29 of document portal is owned by Casey. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-024:T6:rule:630` score=0.000125
  - old: "Cycle 25 of order tracking is owned by Taylor. Data verification is not yet complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 25 of order tracking is owned by Taylor. Data verification is already complete. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T6 / D_NLI

- `syn-zh-016:T6:rule:244` score=0.997607
  - old: "庫存同步第17輪交付由家豪負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "家豪負責庫存同步第17輪的交付工作。驗收持續受到權限問題阻礙。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-012:T6:rule:232` score=0.997684
  - old: "帳務核對第13輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "雅婷負責帳務核對第13輪的交付工作。驗收持續受到權限問題阻礙。交付預計在2026-11-10進行，最晚須於2026-11-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
- `syn-zh-012:T6:rule:231` score=0.997880
  - old: "帳務核對第13輪交付由雅婷負責。權限問題不再阻礙驗收。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "帳務核對第13輪交付由雅婷負責。驗收持續受到權限問題阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-002:T6:rule:221` score=0.997912
  - old: "身分驗證第3輪交付由雅婷負責。目前驗收沒有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第3輪交付由雅婷負責。目前驗收有阻礙。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-015:T6:rule:241` score=0.997914
  - old: "付款服務第16輪交付由怡君負責。權限問題不再阻礙驗收。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "怡君負責付款服務第16輪的交付工作。驗收持續受到權限問題阻礙。交付預計在2026-12-10進行，最晚須於2026-12-28完成。這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。"
### T7 / A

- `syn-zh-074:T7:rule:318` score=0.020202
  - old: "客服工作台第75輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "客服工作台第75輪交付由品妤負責。目前進度落後計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-060:T7:rule:290` score=0.020408
  - old: "付款服務第61輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第61輪交付由怡君負責。目前進度落後計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-061:T7:rule:292` score=0.020408
  - old: "庫存同步第62輪交付由家豪負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第62輪交付由家豪負責。目前進度落後計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-062:T7:rule:294` score=0.020408
  - old: "身分驗證第63輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第63輪交付由雅婷負責。目前進度落後計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-063:T7:rule:296` score=0.020408
  - old: "報表匯出第64輪交付由柏宇負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "報表匯出第64輪交付由柏宇負責。目前進度落後計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T7 / B768

- `syn-en-068:T7:rule:691` score=0.005613
  - old: "Cycle 69 of access control is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 69 of access control is owned by Casey. Progress is currently behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-065:T7:rule:685` score=0.005682
  - old: "Cycle 66 of notifications is owned by Alex. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 66 of notifications is owned by Alex. Progress is currently behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-067:T7:rule:689` score=0.005891
  - old: "Cycle 68 of backup recovery is owned by Jordan. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 68 of backup recovery is owned by Jordan. Progress is currently behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-074:T7:rule:703` score=0.006602
  - old: "Cycle 75 of support console is owned by Taylor. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 75 of support console is owned by Taylor. Progress is currently behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-064:T7:rule:683` score=0.006740
  - old: "Cycle 65 of data migration is owned by Taylor. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 65 of data migration is owned by Taylor. Progress is currently behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T7 / B256

- `syn-en-065:T7:rule:685` score=0.005311
  - old: "Cycle 66 of notifications is owned by Alex. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 66 of notifications is owned by Alex. Progress is currently behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-068:T7:rule:691` score=0.005506
  - old: "Cycle 69 of access control is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 69 of access control is owned by Casey. Progress is currently behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-067:T7:rule:689` score=0.005539
  - old: "Cycle 68 of backup recovery is owned by Jordan. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 68 of backup recovery is owned by Jordan. Progress is currently behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-074:T7:rule:703` score=0.006114
  - old: "Cycle 75 of support console is owned by Taylor. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 75 of support console is owned by Taylor. Progress is currently behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-069:T7:rule:693` score=0.006355
  - old: "Cycle 70 of order tracking is owned by Taylor. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 70 of order tracking is owned by Taylor. Progress is currently behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T7 / C_classification

- `syn-en-070:T7:rule:696` score=0.000172
  - old: "Cycle 71 of monitoring is owned by Alex. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 71 of monitoring is owned by Alex. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-068:T7:rule:692` score=0.000223
  - old: "Cycle 69 of access control is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 69 of access control is owned by Casey. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-067:T7:rule:690` score=0.000317
  - old: "Cycle 68 of backup recovery is owned by Jordan. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 68 of backup recovery is owned by Jordan. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-073:T7:rule:702` score=0.000402
  - old: "Cycle 74 of document portal is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 74 of document portal is owned by Casey. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-063:T7:rule:682` score=0.000461
  - old: "Cycle 64 of report export is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 64 of report export is owned by Casey. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T7 / C_search_query

- `syn-en-062:T7:rule:680` score=0.001610
  - old: "Cycle 63 of authentication is owned by Jordan. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 63 of authentication is owned by Jordan. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-068:T7:rule:692` score=0.001865
  - old: "Cycle 69 of access control is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 69 of access control is owned by Casey. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-070:T7:rule:696` score=0.002475
  - old: "Cycle 71 of monitoring is owned by Alex. Progress is currently ahead of schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 71 of monitoring is owned by Alex. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-063:T7:rule:682` score=0.002522
  - old: "Cycle 64 of report export is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 64 of report export is owned by Casey. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-073:T7:rule:702` score=0.003339
  - old: "Cycle 74 of document portal is owned by Casey. Progress is currently ahead of schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 74 of document portal is owned by Casey. Progress has shifted from ahead to behind schedule. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T7 / D_NLI

- `syn-zh-074:T7:rule:319` score=0.995425
  - old: "客服工作台第75輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "客服工作台第75輪交付由品妤負責。目前進度已從領先轉為落後。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-064:T7:rule:299` score=0.995440
  - old: "資料搬遷第65輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第65輪交付由品妤負責。目前進度已從領先轉為落後。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-070:T7:rule:311` score=0.995666
  - old: "監控平台第71輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "監控平台第71輪交付由怡君負責。目前進度已從領先轉為落後。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-071:T7:rule:313` score=0.995679
  - old: "稽核記錄第72輪交付由家豪負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第72輪交付由家豪負責。目前進度已從領先轉為落後。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-061:T7:rule:293` score=0.995735
  - old: "庫存同步第62輪交付由家豪負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第62輪交付由家豪負責。目前進度已從領先轉為落後。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T8 / A

- `syn-zh-089:T8:rule:362` score=0.019231
  - old: "客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "客服工作台第90輪交付由品妤負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-075:T8:rule:320` score=0.019417
  - old: "付款服務第76輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "付款服務第76輪交付由怡君負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-076:T8:rule:323` score=0.019417
  - old: "庫存同步第77輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第77輪交付由家豪負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-077:T8:rule:326` score=0.019417
  - old: "身分驗證第78輪交付由雅婷負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第78輪交付由雅婷負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-078:T8:rule:329` score=0.019417
  - old: "報表匯出第79輪交付由柏宇負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "報表匯出第79輪交付由柏宇負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T8 / B768

- `syn-zh-086:T8:rule:353` score=0.005532
  - old: "稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第87輪交付由家豪負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-en-089:T8:rule:747` score=0.006240
  - old: "Cycle 90 of support console is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 90 of support console is owned by Taylor. This document records the blocked delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-087:T8:rule:741` score=0.006294
  - old: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 88 of billing checks is owned by Jordan. This document records the blocked delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-082:T8:rule:726` score=0.006344
  - old: "Cycle 83 of backup recovery is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 83 of backup recovery is owned by Jordan. This document records the blocked delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-081:T8:rule:723` score=0.006685
  - old: "Cycle 82 of search indexing is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 82 of search indexing is owned by Morgan. This document records the blocked delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T8 / B256

- `syn-zh-086:T8:rule:353` score=0.004748
  - old: "稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第87輪交付由家豪負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-en-087:T8:rule:741` score=0.005912
  - old: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 88 of billing checks is owned by Jordan. This document records the blocked delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-089:T8:rule:747` score=0.005976
  - old: "Cycle 90 of support console is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 90 of support console is owned by Taylor. This document records the blocked delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-zh-082:T8:rule:341` score=0.006067
  - old: "備份還原第83輪交付由雅婷負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "備份還原第83輪交付由雅婷負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-079:T8:rule:332` score=0.006091
  - old: "資料搬遷第80輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第80輪交付由品妤負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T8 / C_classification

- `syn-zh-079:T8:rule:332` score=0.006000
  - old: "資料搬遷第80輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第80輪交付由品妤負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-086:T8:rule:353` score=0.006623
  - old: "稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第87輪交付由家豪負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-085:T8:rule:350` score=0.006977
  - old: "監控平台第86輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "監控平台第86輪交付由怡君負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-085:T8:rule:351` score=0.007005
  - old: "監控平台第86輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "監控平台第86輪交付由怡君負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。目前資料授權尚未取得，阻礙本輪交付。"
- `syn-zh-077:T8:rule:326` score=0.007290
  - old: "身分驗證第78輪交付由雅婷負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第78輪交付由雅婷負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T8 / C_search_query

- `syn-zh-079:T8:rule:332` score=0.004875
  - old: "資料搬遷第80輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第80輪交付由品妤負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-086:T8:rule:353` score=0.005451
  - old: "稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第87輪交付由家豪負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-077:T8:rule:326` score=0.005805
  - old: "身分驗證第78輪交付由雅婷負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "身分驗證第78輪交付由雅婷負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-076:T8:rule:323` score=0.005948
  - old: "庫存同步第77輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第77輪交付由家豪負責。文件記錄本輪受阻交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-en-087:T8:rule:743` score=0.006082
  - old: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting.\n\nData access has not been approved, blocking delivery. Final validation cannot proceed and delivery must be postponed. The owner is tracking the access request; validation can only be rescheduled after approval."
### T8 / D_NLI

- `syn-en-084:T8:rule:734` score=0.001111
  - old: "Cycle 85 of order tracking is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 85 of order tracking is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting.\n\nData access has not been approved, blocking delivery. Final validation cannot proceed and delivery must be postponed. The owner is tracking the access request; validation can only be rescheduled after approval."
- `syn-en-086:T8:rule:740` score=0.002462
  - old: "Cycle 87 of audit logging is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 87 of audit logging is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting.\n\nData access has not been approved, blocking delivery. Final validation cannot proceed and delivery must be postponed. The owner is tracking the access request; validation can only be rescheduled after approval."
- `syn-en-076:T8:rule:710` score=0.002848
  - old: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 77 of stock sync is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting.\n\nData access has not been approved, blocking delivery. Final validation cannot proceed and delivery must be postponed. The owner is tracking the access request; validation can only be rescheduled after approval."
- `syn-en-082:T8:rule:728` score=0.002977
  - old: "Cycle 83 of backup recovery is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 83 of backup recovery is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting.\n\nData access has not been approved, blocking delivery. Final validation cannot proceed and delivery must be postponed. The owner is tracking the access request; validation can only be rescheduled after approval."
- `syn-en-087:T8:rule:743` score=0.003044
  - old: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting.\n\nData access has not been approved, blocking delivery. Final validation cannot proceed and delivery must be postponed. The owner is tracking the access request; validation can only be rescheduled after approval."
### T9 / A

- `syn-zh-074:T9:rule:383` score=0.090909
  - old: "客服工作台第75輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "客服工作台第75輪交付由品妤負責。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-069:T9:rule:365` score=0.091837
  - old: "訂單追蹤第70輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "訂單追蹤第70輪交付由品妤負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-061:T9:rule:369` score=0.091837
  - old: "庫存同步第62輪交付由家豪負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "庫存同步第62輪交付由家豪負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-065:T9:rule:371` score=0.091837
  - old: "通知佇列第66輪交付由怡君負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "通知佇列第66輪交付由怡君負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-067:T9:rule:376` score=0.091837
  - old: "備份還原第68輪交付由雅婷負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "備份還原第68輪交付由雅婷負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T9 / B768

- `syn-zh-034:T9:rule:384` score=0.010014
  - old: "資料搬遷第35輪交付由品妤負責。目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第35輪交付由品妤負責。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-087:T9:rule:378` score=0.010319
  - old: "帳務核對第88輪交付由雅婷負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "帳務核對第88輪交付由雅婷負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-089:T9:rule:379` score=0.010859
  - old: "客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "客服工作台第90輪交付由品妤負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-086:T9:rule:367` score=0.011203
  - old: "稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第87輪交付由家豪負責。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-081:T9:rule:373` score=0.013656
  - old: "搜尋索引第82輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "搜尋索引第82輪交付由家豪負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T9 / B256

- `syn-zh-034:T9:rule:384` score=0.008532
  - old: "資料搬遷第35輪交付由品妤負責。目前資料核對尚未完成。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "資料搬遷第35輪交付由品妤負責。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-087:T9:rule:378` score=0.009003
  - old: "帳務核對第88輪交付由雅婷負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "帳務核對第88輪交付由雅婷負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-086:T9:rule:367` score=0.009062
  - old: "稽核記錄第87輪交付由家豪負責。文件記錄本輪交付的工作安排。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第87輪交付由家豪負責。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-089:T9:rule:379` score=0.009260
  - old: "客服工作台第90輪交付由品妤負責。文件記錄本輪交付的工作安排。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "客服工作台第90輪交付由品妤負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
- `syn-zh-056:T9:rule:382` score=0.012065
  - old: "稽核記錄第57輪交付由家豪負責。團隊已暫停本輪部署。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "稽核記錄第57輪交付由家豪負責。預計交付日為2026-11-10，截止日期為2026-11-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T9 / C_classification

- `syn-en-084:T9:rule:758` score=0.000079
  - old: "Cycle 85 of order tracking is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 85 of order tracking is owned by Taylor.  The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-081:T9:rule:764` score=0.000100
  - old: "Cycle 82 of search indexing is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 82 of search indexing is owned by Morgan.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-088:T9:rule:765` score=0.000105
  - old: "Cycle 89 of document portal is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 89 of document portal is owned by Casey.  The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-027:T9:rule:750` score=0.000135
  - old: "Cycle 28 of billing checks is owned by Jordan. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 28 of billing checks is owned by Jordan.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-zh-069:T9:rule:365` score=0.000150
  - old: "訂單追蹤第70輪交付由品妤負責。目前進度領先計畫。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
  - new: "訂單追蹤第70輪交付由品妤負責。預計交付日為2026-12-10，截止日期為2026-12-28。本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。"
### T9 / C_search_query

- `syn-en-081:T9:rule:764` score=0.000252
  - old: "Cycle 82 of search indexing is owned by Morgan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 82 of search indexing is owned by Morgan.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-084:T9:rule:758` score=0.000275
  - old: "Cycle 85 of order tracking is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 85 of order tracking is owned by Taylor.  The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-088:T9:rule:765` score=0.000342
  - old: "Cycle 89 of document portal is owned by Casey. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 89 of document portal is owned by Casey.  The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-033:T9:rule:761` score=0.000395
  - old: "Cycle 34 of report export is owned by Casey. Data verification is not yet complete. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 34 of report export is owned by Casey.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-087:T9:rule:757` score=0.000399
  - old: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 88 of billing checks is owned by Jordan.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
### T9 / D_NLI

- `syn-en-002:T9:rule:766` score=0.014309
  - old: "Cycle 3 of authentication is owned by Jordan. The review currently has no blockers. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 3 of authentication is owned by Jordan.  The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-089:T9:rule:755` score=0.016044
  - old: "Cycle 90 of support console is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 90 of support console is owned by Taylor.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-084:T9:rule:758` score=0.018559
  - old: "Cycle 85 of order tracking is owned by Taylor. This document records the delivery arrangements. The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 85 of order tracking is owned by Taylor.  The planned delivery is 2026-11-10; the deadline is 2026-11-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-075:T9:rule:754` score=0.019532
  - old: "Cycle 76 of payments is owned by Alex. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 76 of payments is owned by Alex.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
- `syn-en-087:T9:rule:757` score=0.023115
  - old: "Cycle 88 of billing checks is owned by Jordan. This document records the delivery arrangements. The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."
  - new: "Cycle 88 of billing checks is owned by Jordan.  The planned delivery is 2026-12-10; the deadline is 2026-12-28. The named owner will check test results, dependency lists, and handover records at the team meeting."

## Q1–Q8

- Q1: T8 與固定負例的 B AUROC 見主表；不將 T1/T2/T3/T4 當正例。
- Q2: T6/T7 的 B AUROC 見主表；有實際 B 分數才產生分布圖。
- Q3: 兩種 C prefix 均列出；C−B 差異見下表。不用 T7 選 prefix。
- Q4: D_NLI T6/T7 見主表；無法外推至 Decision Maker。
- Q5: 五種中文形態各列主表；不能只由 AUROC 宣稱『完全看不見』。
- Q6: 雜訊表列 batch size／順序改變後的三次量測；未跑不填零。
- Q7: 靈敏度表只使用實測 B 距離；圖只在有數據時產生。
- Q8: T7 是 holdout，主表固定呈現；差距 <0.05 視為打平。

| category | C classification − B | C search query − B |
|---|---|---|
| T5 | +0.219 | +0.076 |
| T6 | +0.324 | +0.297 |
| T6-zh-沒有 | +0.383 | +0.374 |
| T6-zh-不再 | +0.294 | +0.205 |
| T6-zh-尚未 | +0.296 | +0.206 |
| T6-zh-取消 | +0.413 | +0.419 |
| T6-zh-暫停 | +0.368 | +0.383 |
| T6-en | +0.298 | +0.276 |
| T7 | +0.429 | +0.493 |
| T8 | +0.274 | +0.258 |

## H1–H7

假說定義以 docs/protocol-v0.1.md 為準。數量不足或 diagnostic 時禁止給出保留／淘汰結論。

此節檢查原交接要求的真實底稿／雙生成器實驗是否完整；本合成集上的限定假說對照見 [summary.md](summary.md)。

- H1: 無法判定（資料覆蓋不足；缺少：無）。
- H2: 無法判定（資料覆蓋不足；缺少：無）。
- H3: 無法判定（資料覆蓋不足；缺少：無）。
- H4: 無法判定（資料覆蓋不足；缺少：無）。
- H5: 無法判定（資料覆蓋不足；缺少：B2, E）。
- H6: 無法判定（資料覆蓋不足；缺少：無）。
- H7: 無法判定（資料覆蓋不足；缺少：無）。

"""Descriptive synthetic-pilot analysis, never a population performance claim."""
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
from .common import CONTROL, ZH_FORMS, read_jsonl
from .report import metric

ARMS = ["A", "B768", "B256", "C_classification", "C_search_query", "D_NLI"]
CATS = ["T5", "T6", "T7", "T8"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    root = Path(args.run_dir)
    manifest = json.loads((root / "manifest.json").read_text())
    if not manifest.get("synthetic") or manifest["status"] != "completed":
        raise ValueError("Require a completed synthetic pilot")
    rows = read_jsonl(root / "pairs.jsonl")
    scores = {s["pair_id"]: s for s in read_jsonl(root / "scores.jsonl")}
    if any(any(a not in scores.get(r["pair_id"], {}) for a in ARMS) for r in rows):
        raise ValueError("Missing score: do not claim full comparison")
    tables = {lang: {c: {a: metric([r for r in rows if lang == "all" or r["lang"] == lang], scores, c, a)
                         for a in ARMS} for c in CATS} for lang in ("all", "zh", "en")}
    strength_tables = {strength: {c: {a: metric([r for r in rows if r["category"] in CONTROL or r["strength"] == strength], scores, c, a)
                                      for a in ARMS} for c in ("T6", "T7", "T8")}
                       for strength in ("word", "sentence", "paragraph")}
    noise = read_jsonl(root / "noise.jsonl")
    threshold = max(n["p95"] for n in noise)
    negation = []
    for form in ZH_FORMS:
        selected = [r for r in rows if r["subcategory"] == "T6-zh-" + form]
        values = [scores[r["pair_id"]]["B768"] for r in selected]
        negation.append({"form": form, "n": len(selected), "B_mean": float(np.mean(values)),
                         "B_above_noise_fraction": float(np.mean(np.array(values) > threshold)),
                         **{a: metric(rows, scores, "T6-zh-"+form, a)["auc"] for a in ARMS}})
    argmax = []
    for c in ["negative", *CATS]:
        selected = [r for r in rows if (r["category"] in CONTROL if c == "negative" else r["category"] == c)]
        argmax.append({"category": c, "n": len(selected), **{
            prefix: float(np.mean([scores[r["pair_id"]][f"C_{prefix}_argmax"] for r in selected]))
            for prefix in ("classification", "search_query")}})
    def value(c, a):
        return tables["all"][c][a]["auc"]
    def relation(c, a, b):
        delta = value(c, a) - value(c, b)
        return 0 if abs(delta) < .05 else (1 if delta > 0 else -1)
    inversions, changed = [], []
    for a, b in itertools.combinations(ARMS, 2):
        x, y = relation("T6", a, b), relation("T7", a, b)
        if x != y:
            changed.append({"a": a, "b": b, "T6_relation": x, "T7_relation": y})
        if x*y == -1:
            inversions.append([a, b])
    output = {"tables": tables, "strength_tables": strength_tables, "negation": negation, "argmax_change_rate": argmax,
              "noise_threshold": threshold, "holdout_relation_changes": changed, "holdout_strict_inversions": inversions}
    (root / "summary.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    lines = ["# EG2 合成資料試驗結果", "", "**此輪為規則模板生成的合成底稿試驗；不是原規格要求的真實文件＋雙生成器實驗。**",
             "", f"資料：建立 180 段合成底稿，其中 {len({r['base_id'] for r in rows})} 段實際用於 {len(rows)} 組比較，中英各半；固定 seed 20261014。所有模型 CPU float32。",
             "已跑 A、B768、B256、C 的兩種 prefix、D_NLI。D 是 multilingual NLI 替代，並非 Decision Maker。B2、E 未跑。",
             "生成器全部為 rule，無 Gemini 生成或獨立覆核；標籤依構造時明確狀態及截止日期設定。",
             "資料與分析計畫在主要評分前固定，沒有依 T7 結果調整設定。", ""]
    for lang, table in tables.items():
        lines += [f"## AUROC（{lang}）", "", "| 類別 | 正／負例數 | " + " | ".join(ARMS) + " |", "|---|---|"+"---|"*len(ARMS)]
        for c in CATS:
            sample = table[c]["A"]
            lines.append(f"| {c} | {sample['n_positive']}/{sample['n_negative']} | " + " | ".join(f"{table[c][a]['auc']:.3f}" for a in ARMS) + " |")
        lines.append("")
    lines += ["負例固定為 T1+T2+T3+T4；T0/T9 不進 AUROC。語言子表的正負例都限制為同一語言。", "",
              "## Q1–Q8", "",
              f"- Q1：新增阻礙 T8，B768 AUROC={value('T8','B768'):.3f}，A={value('T8','A'):.3f}。",
              f"- Q2：B768 否定 T6={value('T6','B768'):.3f}，反義 T7={value('T7','B768'):.3f}。距離分布見 fig/T6.png、fig/T7.png。",
              "- Q3：C−B 的分類別差值如下表；兩種 prefix 均保留，不用 holdout 挑選。",
              f"- Q4：D_NLI 否定 T6={value('T6','D_NLI'):.3f}，反義 T7={value('T7','D_NLI'):.3f}；不能外推到 Decision Maker。",
              "- Q5：五種中文否定如下表。距離高於噪音只表示有變動，不等於能與無狀態變化區分。",
              f"- Q6：100 筆 T0 以 batch 1/8/32 及不同順序重跑，最大 p95={threshold:.3g}；完整 mean/std/p95/max 見下表。",
              "- Q7：word/sentence/paragraph 距離曲線見 fig/sensitivity.png 與完整報表。word 是短詞級編輯，不保證 tokenizer token 數恰為 1。",
              f"- Q8：以 <0.05 視為平手，T6→T7 有 {len(changed)} 組兩兩關係改變，其中 {len(inversions)} 組嚴格排序翻轉；見 summary.json。", "",
              "| 類別 | C classification − B768 | C search query − B768 |", "|---|---|---|"]
    for c in CATS:
        lines.append(f"| {c} | {value(c,'C_classification')-value(c,'B768'):+.3f} | {value(c,'C_search_query')-value(c,'B768'):+.3f} |")
    lines += ["", "| 中文形態 | n | B768 AUROC | D_NLI AUROC | B 距離 mean | 高於噪音比例 |", "|---|---|---|---|---|---|"]
    for n in negation:
        lines.append(f"| {n['form']} | {n['n']} | {n['B768']:.3f} | {n['D_NLI']:.3f} | {n['B_mean']:.6g} | {n['B_above_noise_fraction']:.1%} |")
    lines += ["", "| run | batch | n | mean | std | p95 | max |", "|---|---|---|---|---|---|---|"]
    for n in noise:
        lines.append(f"| {n['run']} | {n['batch_size']} | {n['n']} | {n['mean']:.3g} | {n['std']:.3g} | {n['p95']:.3g} | {n['max']:.3g} |")
    lines += ["", "C 的 argmax 移動比例（不是 AUROC）：", "", "| category | n | Classification | SearchQuery |", "|---|---|---|---|"]
    for a in argmax:
        lines.append(f"| {a['category']} | {a['n']} | {a['classification']:.1%} | {a['search_query']:.1%} |")
    lines += ["", "依正例擾動強度分層的 AUROC（負例仍為固定 270 筆，不是等字數配對比較）：", "",
              "| category | strength | n positive | " + " | ".join(ARMS) + " |", "|---|---|---|"+"---|"*len(ARMS)]
    for strength, table in strength_tables.items():
        for c, values in table.items():
            lines.append(f"| {c} | {strength} | {values['A']['n_positive']} | " + " | ".join("未跑／無此分層" if values[a]["auc"] is None else f"{values[a]['auc']:.3f}" for a in ARMS) + " |")
    h1 = value("T8", "B768") > .85 and value("T8", "B768")-value("T8", "A") >= .05
    h2 = all(value(c,"B768") < .65 for c in ("T6","T7"))
    h4 = all(value(c,"D_NLI") > .8 for c in ("T6","T7"))
    h3_details = []
    for prefix in ("C_classification", "C_search_query"):
        between = all(min(value(c,"B768"), value(c,"D_NLI")) <= value(c,prefix) <= max(value(c,"B768"),value(c,"D_NLI")) for c in ("T6","T7"))
        ties_b = all(abs(value(c,prefix)-value(c,"B768")) < .05 for c in ("T6","T7"))
        h3_details.append(f"{prefix}：兩類皆介於 B/D 之間={'是' if between else '否'}；兩類皆與 B 打平={'是' if ties_b else '否'}")
    h5_tested = all(value("T5",a) < .7 for a in ARMS)
    h5_counterexamples = [f"{a}={value('T5',a):.3f}" for a in ARMS if value("T5",a) >= .7]
    h5_text = ("已測方法都 <0.70，但 B2/E 未跑，尚不能支持『所有 arm』。" if h5_tested else
               "本合成集出現反例，原『所有 arm 都 <0.70』預測不成立：" + "、".join(h5_counterexamples) + "。B2/E 未跑不會消除這個反例；不補猜測解釋。")
    lines += ["", "## H1–H7：只對照本合成集", "",
              f"- H1：{'符合' if h1 else '不符合'} B(T8)>0.85 且比 A 高至少 0.05。這裡以既定平手規則解讀差距，沒有宣稱統計顯著；不據此淘汰整條技術路線。",
              f"- H2：{'符合' if h2 else '不符合'} B(T6)、B(T7) 都 <0.65 的預測；只記錄觀察，不猜測原因。",
              "- H3：" + "；".join(h3_details) + "。",
              f"- H4：{'符合' if h4 else '不符合'} D(T6)、D(T7) 都 >0.80；只適用本 NLI 模型，不能宣稱 Decision Maker 成立或失敗。",
              "- H5：" + h5_text,
              "- H6：無法判定，沒有另一個 LLM 生成器；不能排除模板指紋。",
              f"- H7：{'本資料上的兩兩排序關係維持' if not changed else '本資料上的兩兩排序關係未完全維持'}；0.05 以內算平手。", "",
              "## 適用範圍與重現", "",
              "- 同一底稿跨擾動強度重複出現；中英有對應模板，樣本並非獨立，不能把 770 當作 770 個獨立真實專案。",
              "- 五種中文否定每類 15 筆實際來自 5 個底稿 × 3 種強度；文字模板更少。",
              "- 日期負例/正例編輯字元數不完全相同；T8 長段落也改更多字。A baseline 與分強度表用來揭露這些混雜因素。",
              "- T6 的長段落版本同時改述背景，總 AUROC 混合了語意翻轉與改述強度；另看 word 子集。",
              "- T9 中有 12/40 筆只刪中性安排句，並非關鍵狀態句，不能拿來回答關鍵狀態刪除問題；全部 T9 原本就排除 AUROC，未事後改標籤或調整評分資料。",
              "- 另由生成程式作者覆核每類 5 個 B 極端樣本，共 45 筆，紀錄在 author-audit-sample.jsonl；這不是獨立審查。",
              "- 本輪沒有調分類門檻、沒有 precision，也沒有真實資料驗證。AUROC <0.5 按原方向呈現，不事後翻轉分數。",
              "- 每類／arm 的最多 5 個極端樣本見 [完整報表](report.md)，原文與分數均保留。",
              "- 模型 ID、revision、精度、套件版本、輸入 hash 見 manifest.json；資料 recipe 與分析計畫在 data/synthetic-v1/。", ""]
    (root / "summary.md").write_text("\n".join(lines) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matrix = np.array([[value(c,a) for a in ARMS] for c in CATS])
    fig, ax = plt.subplots(figsize=(10,4))
    im = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(len(ARMS)), ["Diff A", "EG2 768", "EG2 256", "C Class.", "C Search", "D NLI"])
    ax.set_yticks(range(len(CATS)), ["T5 Dates", "T6 Negation", "T7 Antonym", "T8 Blocker"])
    for y in range(len(CATS)):
        for x in range(len(ARMS)):
            ax.text(x,y,f"{matrix[y,x]:.3f}",ha="center",va="center",color="black" if matrix[y,x]>.6 else "white")
    ax.set_title("Synthetic rule-template pilot / AUROC (not real-document validation)")
    fig.colorbar(im, ax=ax, label="AUROC")
    fig.tight_layout()
    fig.savefig(root / "fig" / "auc-summary.png", dpi=180)
    plt.close(fig)
    print(root / "summary.md")


if __name__ == "__main__":
    main()

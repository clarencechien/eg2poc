import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
from .common import CONTROL, POSITIVE, ZH_FORMS, read_jsonl

ARMS = ["A", "B768", "B256", "B2", "C_classification", "C_search_query", "D_NLI", "E"]


def metric(rows, scores, category, arm, generator=None):
    def matches(p):
        if category == "T6-en":
            return p["category"] == "T6" and p["lang"] == "en"
        if category.startswith("T6-zh-"):
            return p["subcategory"] == category
        return p["category"] == category
    positives = [p for p in rows if matches(p) and p["label"] == 1 and not p["ambiguous"]]
    negatives = [p for p in rows if p["category"] in CONTROL and p["label"] == 0 and not p["ambiguous"]]
    if generator:
        positives = [p for p in positives if p["generator"] == generator]
        negatives = [p for p in negatives if p["generator"] == generator]
    selected = positives + negatives
    selected = [p for p in selected if scores.get(p["pair_id"], {}).get(arm) is not None]
    values = [scores[p["pair_id"]][arm] for p in selected]
    if any(not np.isfinite(v) for v in values):
        raise ValueError("Nonfinite score")
    n_pos = sum(p["label"] == 1 for p in selected)
    n_neg = sum(p["label"] == 0 for p in selected)
    auc = float(roc_auc_score([p["label"] for p in selected], values)) if n_pos and n_neg else None
    return {"auc": auc, "n_positive": n_pos, "n_negative": n_neg}


def cell(m):
    return "未跑／樣本不足" if m["auc"] is None else f"{m['auc']:.3f} ({m['n_positive']}/{m['n_negative']})"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    args = p.parse_args()
    root = Path(args.run_dir)
    manifest = json.loads((root / "manifest.json").read_text())
    rows = read_jsonl(root / "pairs.jsonl")
    scores = {s["pair_id"]: s for s in read_jsonl(root / "scores.jsonl")}
    noise = read_jsonl(root / "noise.jsonl") if (root / "noise.jsonl").exists() else []
    categories = ["T5", "T6"] + [f"T6-zh-{form}" for form in ZH_FORMS] + ["T6-en", "T7", "T8"]
    metrics = {g: {c: {a: metric(rows, scores, c, a, None if g == "all" else g) for a in ARMS}
                   for c in categories} for g in ("all", "rule", "llm")}
    (root / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    diagnostic = manifest["diagnostic"]
    synthetic = manifest.get("synthetic", False)
    lines = ["# EG2 狀態漂移實驗報表", "",
             "**僅為測試程式的人工 fixture；不是正式實驗，禁止用來判定 H1–H7。**" if diagnostic else
             ("**規則模板合成底稿試驗：可觀察本資料上的表現，不能外推真實文件或排除生成器指紋。**" if synthetic else "受控資料執行結果；請同時檢查資料覆蓋與未執行項目。"), "",
             f"執行狀態：{manifest['status']}。樣本數：{len(rows)}。", "",
             "D_NLI 表示 NLI 替代，並非 Decision Maker。E 僅在抽樣子集計分；各格括號為正例／負例數，不可直接與全量結果排序。",
             "T9 不納入 AUROC；固定負例為 T1+T2+T3+T4。缺少一個 class 不計算 AUROC。", "",
             "## 覆蓋缺口", ""]
    lines += [f"- {x}" for x in manifest["coverage_issues"]] or ["無數量缺口。"]
    for generator, table in metrics.items():
        lines += ["", f"## AUROC：{generator}", "", "| 類別 | " + " | ".join(ARMS) + " |",
                  "|---|" + "---|" * len(ARMS)]
        for c, values in table.items():
            lines.append("| " + c + " | " + " | ".join(cell(values[a]) for a in ARMS) + " |")
    lines += ["", "## Q6 雜訊底線", "", "| run | batch | n | mean | std | p95 | max |", "|---|---|---|---|---|---|---|"]
    for n in noise:
        lines.append("| " + " | ".join(str(n[k]) for k in ("run", "batch_size", "n", "mean", "std", "p95", "max")) + " |")
    if not noise:
        lines.append("| 未跑 | — | — | — | — | — | — |")
    lines += ["", "## Q7 靈敏度", "", "| 類別 | strength | n | B mean | B p50 | 超過 noise p95 比例 |", "|---|---|---|---|---|---|"]
    sensitivity = []
    for c in ("T3", "T6", "T8"):
        for strength in ("word", "sentence", "paragraph"):
            values = [scores[r["pair_id"]]["B768"] for r in rows if r["category"] == c and r["strength"] == strength and "B768" in scores.get(r["pair_id"], {})]
            if values and noise:
                threshold = max(n["p95"] for n in noise)
                entry = (c, strength, len(values), float(np.mean(values)), float(np.median(values)), float(np.mean(np.array(values) > threshold)))
                sensitivity.append(entry)
                lines.append("| " + " | ".join(map(str, entry)) + " |")
            else:
                lines.append(f"| {c} | {strength} | {len(values)} | 未跑 | 未跑 | 未跑 |")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig_dir = root / "fig"
    fig_dir.mkdir(exist_ok=True)
    for c in sorted(CONTROL | POSITIVE):
        values = [scores[r["pair_id"]]["B768"] for r in rows if r["category"] == c and "B768" in scores.get(r["pair_id"], {})]
        if not values:
            continue
        fig, ax = plt.subplots()
        ax.hist(values, bins=20, alpha=.6, label="B768 distance")
        if noise:
            ax.hist([v for n in noise for v in n["distances"]], bins=20, alpha=.5, label="T0 repeated distance")
        ax.set_xlabel("Cosine distance (B/T0)")
        ax.set_ylabel("Count")
        if c in {"T6", "T7"}:
            d = [scores[r["pair_id"]]["D_NLI"] for r in rows if r["category"] == c and "D_NLI" in scores.get(r["pair_id"], {})]
            if d:
                other = ax.twiny()
                other.hist(d, bins=20, histtype="step", color="red", label="D_NLI")
                other.set_xlabel("D contradiction probability (separate scale)")
                other.legend(loc="upper right")
        ax.set_title(c + (" / diagnostic fixture" if diagnostic else ""))
        ax.legend(loc="upper left")
        fig.tight_layout()
        fig.savefig(fig_dir / f"{c}.png")
        plt.close(fig)
    if sensitivity:
        fig, ax = plt.subplots()
        for c in ("T3", "T6", "T8"):
            subset = [s for s in sensitivity if s[0] == c]
            ax.plot([s[1] for s in subset], [s[3] for s in subset], marker="o", label=c)
        ax.set_ylabel("Mean B768 distance")
        ax.legend()
        fig.savefig(fig_dir / "sensitivity.png")
        plt.close(fig)
    lines += ["", "## 每類／arm 最極端樣本（最多 5 筆；需人工覆核）", ""]
    for c in sorted(CONTROL | POSITIVE | {"T9"}):
        for a in ARMS:
            selected = [r for r in rows if r["category"] == c and scores.get(r["pair_id"], {}).get(a) is not None]
            selected.sort(key=lambda r: scores[r["pair_id"]][a], reverse=c in CONTROL)
            if selected:
                lines += [f"### {c} / {a}", ""]
                for r in selected[:5]:
                    lines += [f"- `{r['pair_id']}` score={scores[r['pair_id']][a]:.6f}",
                              "  - old: " + json.dumps(r["old_text"], ensure_ascii=False),
                              "  - new: " + json.dumps(r["new_text"], ensure_ascii=False)]
    lines += ["", "## Q1–Q8", ""]
    q = {1: "T8 與固定負例的 B AUROC 見主表；不將 T1/T2/T3/T4 當正例。",
         2: "T6/T7 的 B AUROC 見主表；有實際 B 分數才產生分布圖。",
         3: "兩種 C prefix 均列出；C−B 差異見下表。不用 T7 選 prefix。",
         4: "D_NLI T6/T7 見主表；無法外推至 Decision Maker。",
         5: "五種中文形態各列主表；不能只由 AUROC 宣稱『完全看不見』。",
         6: "雜訊表列 batch size／順序改變後的三次量測；未跑不填零。",
         7: "靈敏度表只使用實測 B 距離；圖只在有數據時產生。",
         8: "T7 是 holdout，主表固定呈現；差距 <0.05 視為打平。"}
    for i, answer in q.items():
        lines.append(f"- Q{i}: " + ("正式實驗未跑；" if diagnostic else "") + answer)
    lines += ["", "| category | C classification − B | C search query − B |", "|---|---|---|"]
    for c in categories:
        b = metrics["all"][c]["B768"]["auc"]
        vals = [metrics["all"][c][a]["auc"] for a in ("C_classification", "C_search_query")]
        lines.append("| " + c + " | " + " | ".join("未跑" if b is None or v is None else f"{v-b:+.3f}" for v in vals) + " |")
    lines += ["", "## H1–H7", "", "假說定義以 docs/protocol-v0.1.md 為準。數量不足或 diagnostic 時禁止給出保留／淘汰結論。", ""]
    if synthetic:
        lines += ["此節檢查原交接要求的真實底稿／雙生成器實驗是否完整；本合成集上的限定假說對照見 [summary.md](summary.md)。", ""]
    requirements = {1: ["B768", "A"], 2: ["B768"], 3: ["B768", "C_classification", "C_search_query", "D_NLI"],
                    4: ["D_NLI"], 5: ARMS, 6: ["B768", "C_classification", "C_search_query", "D_NLI"],
                    7: ["A", "B768", "C_classification", "C_search_query", "D_NLI"]}
    for h, arms in requirements.items():
        missing = [a for a in arms if not any(a in s for s in scores.values())]
        if diagnostic or manifest["coverage_issues"] or missing:
            lines.append(f"- H{h}: 無法判定（" + ("diagnostic；" if diagnostic else "") +
                         ("資料覆蓋不足；" if manifest["coverage_issues"] else "") + "缺少：" + (", ".join(missing) or "無") + "）。")
        else:
            lines.append(f"- H{h}: 數據已列出，待逐項人工對照事先假說；此程式不自動推論因果或改動門檻。")
    (root / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(root / "report.md")


if __name__ == "__main__":
    main()

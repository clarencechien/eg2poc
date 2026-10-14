"""Fixed, bilingual synthetic pilot. No real-document or LLM provenance claims.

Labels follow explicit constructed facts. Freeze this file and the generated
JSONL before scoring; never edit T7 in response to results.
"""
import json
import random
from collections import Counter
from pathlib import Path
from .common import digest, validate_pairs, write_jsonl
from .gen_rule import make_pair

SEED = 20261014
FORMS = ("沒有", "不再", "尚未", "取消", "暫停")
STATES = {
    "zh": {
        "沒有": ("目前驗收沒有阻礙。", "目前驗收有阻礙。", "目前有問題阻礙驗收。"),
        "不再": ("權限問題不再阻礙驗收。", "權限問題仍然阻礙驗收。", "驗收持續受到權限問題阻礙。"),
        "尚未": ("目前資料核對尚未完成。", "目前資料核對已經完成。", "目前已經完成資料核對。"),
        "取消": ("團隊已取消本輪部署。", "團隊未取消本輪部署。", "本輪部署並未被團隊取消。"),
        "暫停": ("團隊已暫停本輪部署。", "團隊未暫停本輪部署。", "本輪部署並未被團隊暫停。"),
        "ontrack": ("目前進度領先計畫。", "目前進度落後計畫。", "目前進度已從領先轉為落後。"),
        "neutral": ("文件記錄本輪交付的工作安排。", "", ""),
    },
    "en": {
        "沒有": ("The review currently has no blockers.", "The review currently has blockers.", "Unresolved issues currently block the review."),
        "不再": ("The access issue no longer blocks review.", "The access issue still blocks review.", "Review remains blocked by the access issue."),
        "尚未": ("Data verification is not yet complete.", "Data verification is already complete.", "The team has now completed data verification."),
        "取消": ("The team has cancelled deployment.", "The team has not cancelled deployment.", "Deployment has not been cancelled by the team."),
        "暫停": ("The team has paused deployment.", "The team has not paused deployment.", "Deployment has not been paused by the team."),
        "ontrack": ("Progress is currently ahead of schedule.", "Progress is currently behind schedule.", "Progress has shifted from ahead to behind schedule."),
        "neutral": ("This document records the delivery arrangements.", "", ""),
    },
}
PROJECTS = {
    "zh": ["付款服務", "庫存同步", "身分驗證", "報表匯出", "資料搬遷", "通知佇列", "搜尋索引", "備份還原", "權限管理", "訂單追蹤", "監控平台", "稽核記錄", "帳務核對", "文件入口", "客服工作台"],
    "en": ["payments", "stock sync", "authentication", "report export", "data migration", "notifications", "search indexing", "backup recovery", "access control", "order tracking", "monitoring", "audit logging", "billing checks", "document portal", "support console"],
}


def compose(b, status=None, paraphrase=False):
    status = b["status"] if status is None else status
    if b["lang"] == "zh":
        if paraphrase:
            return (f"{b['owner']}負責{b['project']}第{b['cycle']}輪的交付工作。{status}"
                    f"交付預計在{b['planned']}進行，最晚須於{b['deadline']}完成。"
                    "這份紀錄涵蓋測試結果、相依項目清單與交接文件；相關細節會由指定負責人在例會確認。")
        return (f"{b['project']}第{b['cycle']}輪交付由{b['owner']}負責。{status}"
                f"預計交付日為{b['planned']}，截止日期為{b['deadline']}。"
                "本次紀錄包含測試結果、相依項目清單及交接文件，指定負責人會在例會中確認相關細節。")
    if paraphrase:
        return (f"{b['owner']} owns cycle {b['cycle']} of the {b['project']} delivery. {status} "
                f"Delivery is planned for {b['planned']} against a deadline of {b['deadline']}. "
                "The named owner will review test results, dependency lists, and handover records at the team meeting.")
    return (f"Cycle {b['cycle']} of {b['project']} is owned by {b['owner']}. {status} "
            f"The planned delivery is {b['planned']}; the deadline is {b['deadline']}. "
            "The named owner will check test results, dependency lists, and handover records at the team meeting.")


def main():
    root = Path("data/synthetic-v1")
    if root.exists():
        raise FileExistsError("Synthetic corpus is frozen; choose a new version instead of overwriting")
    bases, pairs = [], []
    rng = random.Random(SEED)
    for lang in ("zh", "en"):
        families = [form for form in FORMS for _ in range(12)] + ["ontrack"] * 15 + ["neutral"] * 15
        owners = ["怡君", "家豪", "雅婷", "柏宇", "品妤"] if lang == "zh" else ["Alex", "Morgan", "Jordan", "Casey", "Taylor"]
        lang_bases = []
        for i, family in enumerate(families):
            month = 11 + (i % 2)
            b = {"base_id": f"syn-{lang}-{i:03d}", "doc_id": f"synthetic-{lang}-{i//9:02d}", "para_id": i % 9,
                 "lang": lang, "family": family, "source_kind": "synthetic_rule", "reviewed": True,
                 "project": PROJECTS[lang][i % 15], "owner": owners[i % 5], "cycle": i + 1,
                 "planned": f"2026-{month:02d}-10", "deadline": f"2026-{month:02d}-28",
                 "status": STATES[lang][family][0]}
            b["text"] = compose(b)
            assert 80 <= len(b["text"]) <= 400, len(b["text"])
            lang_bases.append(b)
        bases.extend(lang_bases)

        def add(b, cat, new, strength="word", subcategory=None):
            row = make_pair(b, cat, new, strength, subcategory, str(len(pairs)))
            row.update(ground_truth_verified=True, verification="constructed explicit template facts; no independent LLM review",
                       source_kind="synthetic_rule", template_family=b["family"])
            pairs.append(row)

        sample = rng.sample(lang_bases, len(lang_bases))
        for b in sample[:50]:
            add(b, "T0", b["text"])
        for b in sample[:30]:
            # One non-status typo plus two harmless formatting edits.
            old = b["text"]
            new = old.replace("紀錄", "記錄", 1).replace("交接文件", "交接文仵", 1) if lang == "zh" else old.replace("records", "recrods", 1)
            add(b, "T1", "  " + new + "\n")
        for b in sample[30:60]:
            old = b["text"]
            sep = "。" if lang == "zh" else ". "
            first, rest = old.split(sep, 1)
            add(b, "T2", rest + ("" if lang == "zh" else " ") + first + sep.rstrip(), "paragraph")
        # Fifteen matched sources per language, each at three paraphrase strengths.
        for b in sample[:15]:
            old = b["text"]
            word = old.replace("包含", "涵蓋", 1) if lang == "zh" else old.replace("check", "review", 1)
            sentence = old.replace("指定負責人會在例會中確認相關細節", "相關細節將由指定負責人在例會確認", 1) if lang == "zh" else old.replace("The named owner will check", "The assigned owner will review", 1)
            for strength, new in [("word", word), ("sentence", sentence), ("paragraph", compose(b, paraphrase=True))]:
                add(b, "T3", new, strength)
        # Date edits use only non-cancelled, non-paused, unblocked/neutral bases.
        date_bases = [b for b in lang_bases if b["family"] in {"沒有", "不再", "neutral"}][:30]
        for b in date_bases:
            within = b["planned"][:-2] + "20"
            missed = "2027-01-30"
            add(b, "T4", b["text"].replace(b["planned"], within), "word")
            add(b, "T5", b["text"].replace(b["planned"], missed), "word")
        for form in FORMS:
            for b in [b for b in lang_bases if b["family"] == form][:5]:
                _, flipped, rewritten = STATES[lang][form]
                for strength, new in [("word", compose(b, flipped)), ("sentence", compose(b, rewritten)),
                                      ("paragraph", compose(b, rewritten, paraphrase=True))]:
                    add(b, "T6", new, strength, f"T6-{lang}-{form}")
        # T7 fixed in advance; no prefix selection or tuning uses this category.
        for b in [b for b in lang_bases if b["family"] == "ontrack"]:
            _, flipped, rewritten = STATES[lang]["ontrack"]
            add(b, "T7", compose(b, flipped), "word")
            add(b, "T7", compose(b, rewritten), "sentence")
        # Neutral base avoids contradictory 'on track' and 'blocked' claims in one version.
        for b in [b for b in lang_bases if b["family"] == "neutral"]:
            old = b["text"]
            if lang == "zh":
                word = old.replace("本輪交付的工作安排", "本輪受阻交付的工作安排", 1)
                sentence = old + "目前資料授權尚未取得，阻礙本輪交付。"
                paragraph = old + "\n\n目前資料授權尚未取得，阻礙本輪交付。團隊無法進行最後驗收，因此交付時間必須延後。負責人正在追蹤授權申請，取得許可後才能重新安排驗收。"
            else:
                word = old.replace("delivery arrangements", "blocked delivery arrangements", 1)
                sentence = old + " Delivery is now blocked because data access has not been approved."
                paragraph = old + "\n\nData access has not been approved, blocking delivery. Final validation cannot proceed and delivery must be postponed. The owner is tracking the access request; validation can only be rescheduled after approval."
            for strength, new in [("word", word), ("sentence", sentence), ("paragraph", paragraph)]:
                add(b, "T8", new, strength)
        for b in sample[:20]:
            add(b, "T9", b["text"].replace(b["status"], "", 1), "sentence")
    validate_pairs(pairs)
    assert len(bases) == 180 and len(pairs) == 770
    write_jsonl(root / "base.jsonl", bases)
    write_jsonl(root / "pairs.jsonl", pairs)
    manifest = {"seed": SEED, "base_count": len(bases), "pair_count": len(pairs),
                "category_counts": dict(sorted(Counter(p["category"] for p in pairs).items())),
                "language_counts": dict(Counter(p["lang"] for p in pairs)), "generator": "rule",
                "source": "synthetic templates authored for this pilot; not real documents",
                "independent_llm_validation": False, "holdout": "T7 frozen before scoring; no tuning",
                "ground_truth": "explicit constructed states and deadlines; author checked, not independent",
                "strength_note": "word denotes a short lexical edit; sentence/paragraph may change several tokens",
                "dependence": "Repeated base across strengths; translations and shared templates are correlated",
                "base_sha256": digest(root / "base.jsonl"), "pairs_sha256": digest(root / "pairs.jsonl"),
                "generator_sha256": digest(__file__)}
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

import hashlib
import json
from pathlib import Path

NEGATIVE = {"T0", "T1", "T2", "T3", "T4"}
POSITIVE = {"T5", "T6", "T7", "T8"}
CONTROL = {"T1", "T2", "T3", "T4"}
ZH_FORMS = ("沒有", "不再", "尚未", "取消", "暫停")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path, row):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        import os
        os.fsync(f.fileno())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_pairs(rows):
    seen = set()
    for p in rows:
        for field in ("pair_id", "base_id", "lang", "category", "subcategory", "strength", "generator", "old_text", "new_text", "label", "ambiguous"):
            if field not in p:
                raise ValueError(f"Missing {field}")
        if p["pair_id"] in seen:
            raise ValueError(f"Duplicate pair_id: {p['pair_id']}")
        seen.add(p["pair_id"])
        c = p["category"]
        if c not in NEGATIVE | POSITIVE | {"T9"}:
            raise ValueError(f"Unknown category: {c}")
        expected = None if c == "T9" else int(c in POSITIVE)
        if p["label"] != expected or p["ambiguous"] != (c == "T9"):
            raise ValueError(f"Invalid ground truth: {p['pair_id']}")
        if p["lang"] not in {"zh", "en"} or p["generator"] not in {"rule", "llm"}:
            raise ValueError("Invalid language or generator")
        if p["strength"] not in {"word", "sentence", "paragraph"}:
            raise ValueError("Invalid strength")
        if not p["old_text"].strip() or not p["new_text"].strip():
            raise ValueError("Empty text")
        if (c == "T0") != (p["old_text"] == p["new_text"]):
            raise ValueError(f"Unexpected unchanged/changed pair: {p['pair_id']}")
    return rows


def coverage(rows, bases):
    issues = []
    if not 150 <= len(bases) <= 200:
        issues.append(f"base count {len(bases)}; target 150–200")
    docs = {b.get("doc_id") for b in bases}
    if len(docs) < 20:
        issues.append(f"document count {len(docs)}; target ≥20")
    if any(not 5 <= sum(b.get("doc_id") == d for b in bases) <= 10 for d in docs):
        issues.append("Each document must supply 5–10 selected paragraphs")
    if any(not 80 <= len(b.get("text", "")) <= 400 for b in bases):
        issues.append("Some base paragraphs are outside 80–400 characters")
    for b in bases:
        if b.get("source_kind") != "repository" or not b.get("source_path") or not b.get("source_commit"):
            issues.append("Some bases lack real repository provenance")
            break
    for lang in ("zh", "en"):
        if sum(b.get("lang") == lang for b in bases) < 75:
            issues.append(f"{lang} bases below 75")
    for c in sorted(CONTROL | POSITIVE):
        for lang in ("zh", "en"):
            if sum(p["category"] == c and p["lang"] == lang for p in rows) < 30:
                issues.append(f"{c}/{lang} below 30 pairs")
    if sum(p["category"] == "T0" for p in rows) < 100:
        issues.append("T0 below 100 pairs")
    for form in ZH_FORMS:
        if sum(p["subcategory"] == f"T6-zh-{form}" for p in rows) < 15:
            issues.append(f"T6-zh-{form} below 15 pairs")
    for c in ("T3", "T6", "T8"):
        for strength in ("word", "sentence", "paragraph"):
            if not any(p["category"] == c and p["strength"] == strength for p in rows):
                issues.append(f"Missing {c}/{strength}")
    # The handoff conflicts on all-rule vs half-LLM categories. Enforce its
    # explicitly mixed categories; record other generator coverage in reports.
    for c in ("T5", "T6", "T7"):
        counts = [sum(p["category"] == c and p["generator"] == g for p in rows) for g in ("rule", "llm")]
        if min(counts) == 0 or abs(counts[0] - counts[1]) > 1:
            issues.append(f"{c} rule/llm not balanced: {counts}")
    return issues

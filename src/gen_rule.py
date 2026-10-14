"""Conservative rule candidates. Semantic edits require independent review."""
import argparse
import re
from .common import POSITIVE, read_jsonl, write_jsonl


def make_pair(b, category, new, strength="word", subcategory=None, suffix="0", generator="rule"):
    return {"pair_id": f"{b['base_id']}:{category}:{generator}:{suffix}", "base_id": b["base_id"],
            "lang": b["lang"], "category": category, "subcategory": subcategory,
            "strength": strength, "generator": generator, "old_text": b["text"], "new_text": new,
            "label": None if category == "T9" else int(category in POSITIVE), "ambiguous": category == "T9",
            "ground_truth_verified": category in {"T0", "T1"}}


def generate(bases, edits=()):
    rows = []
    for b in bases:
        old = b["text"]
        rows.append(make_pair(b, "T0", old))
        # Two formatting changes; no spelling corruption of facts or numbers.
        rows.append(make_pair(b, "T1", "  " + old + "\n"))
        sentences = re.split(r"(?<=[。！？.!?])\s+|(?<=[。！？])", old)
        sentences = [s for s in sentences if s.strip()]
        if len(sentences) >= 2:
            new = " ".join(sentences[1:] + sentences[:1])
            if new != old:
                rows.append(make_pair(b, "T2", new, "paragraph"))
    by_id = {b["base_id"]: b for b in bases}
    for i, edit in enumerate(edits):
        b = by_id[edit["base_id"]]
        before, after = edit["before"], edit["after"]
        if not before or b["text"].count(before) != 1:
            raise ValueError("Each annotated edit must match exactly once")
        if edit["category"] not in {"T3", "T4", "T5", "T6", "T7", "T8", "T9"}:
            raise ValueError("Unsupported edit category")
        new = b["text"].replace(before, after, 1)
        if not new.strip() or new == b["text"]:
            raise ValueError("Edit must change nonempty text")
        row = make_pair(b, edit["category"], new, edit["strength"], edit.get("subcategory"), str(i))
        row["review_note"] = edit.get("review_note")
        # A changed date alone never establishes delayed status.
        rows.append(row)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="data/base.jsonl")
    p.add_argument("--edits", help="JSONL annotated exact replacements; see README")
    p.add_argument("--output", default="data/rule-candidates.jsonl")
    args = p.parse_args()
    write_jsonl(args.output, generate(read_jsonl(args.base), read_jsonl(args.edits) if args.edits else []))


if __name__ == "__main__":
    main()

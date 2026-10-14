import unittest
from collections import Counter
from datetime import date
from pathlib import Path
from src.common import digest, read_jsonl, validate_pairs
import json


class SyntheticCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path("data/synthetic-v1")
        cls.bases = read_jsonl(cls.root / "base.jsonl")
        cls.pairs = read_jsonl(cls.root / "pairs.jsonl")

    def test_counts_balance_and_source(self):
        self.assertEqual(len(self.bases), 180)
        self.assertEqual(len(self.pairs), 770)
        self.assertEqual(Counter(p["lang"] for p in self.pairs), {"zh": 385, "en": 385})
        self.assertTrue(all(b["source_kind"] == "synthetic_rule" for b in self.bases))
        self.assertTrue(all(80 <= len(b["text"]) <= 400 for b in self.bases))
        validate_pairs(self.pairs)

    def test_dates_support_assigned_labels(self):
        bases = {b["base_id"]: b for b in self.bases}
        for p in self.pairs:
            if p["category"] not in {"T4", "T5"}:
                continue
            b = bases[p["base_id"]]
            new_date = b["planned"][:-2] + "20" if p["category"] == "T4" else "2027-01-30"
            self.assertEqual(p["new_text"], p["old_text"].replace(b["planned"], new_date))
            self.assertEqual(int(date.fromisoformat(new_date) > date.fromisoformat(b["deadline"])), p["label"])

    def test_negation_strength_coverage(self):
        for form in ["沒有", "不再", "尚未", "取消", "暫停"]:
            rows = [p for p in self.pairs if p["subcategory"] == "T6-zh-"+form]
            self.assertEqual(len(rows), 15)
            self.assertEqual(Counter(p["strength"] for p in rows), {"word": 5, "sentence": 5, "paragraph": 5})

    def test_frozen_corpus_hashes(self):
        manifest = json.loads((self.root / "manifest.json").read_text())
        self.assertEqual(digest(self.root / "base.jsonl"), manifest["base_sha256"])
        self.assertEqual(digest(self.root / "pairs.jsonl"), manifest["pairs_sha256"])
        self.assertEqual(digest("src/gen_synthetic.py"), manifest["generator_sha256"])


if __name__ == "__main__":
    unittest.main()

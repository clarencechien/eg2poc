import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from src.arms import cosine_distance, probabilities, score_a, verified
from src.common import coverage, validate_pairs
from src.gen_rule import generate, make_pair
from src.llm import Gemini
from src.report import metric


BASE = {"base_id": "test", "text": "The project is on track. Delivery is planned for May 10.", "lang": "en"}


class ExperimentTests(unittest.TestCase):
    def test_diff_direction_and_size(self):
        self.assertEqual(score_a("abc", "abc"), 0)
        self.assertAlmostEqual(score_a("abc", "axc"), 1/3)
        self.assertEqual(score_a("abc", "abcdef"), 1)

    def test_cosine_normalization_and_truncation(self):
        self.assertAlmostEqual(cosine_distance([2, 0], [5, 0]), 0)
        self.assertAlmostEqual(cosine_distance([1, 0], [0, 1]), 1)
        with self.assertRaises(ValueError):
            cosine_distance([0, 0], [1, 0])

    def test_label_probability_argmax(self):
        p, argmax = probabilities([1, 0], [[1, 0], [0, 1], [-1, 0], [0, -1]], .045)
        self.assertEqual(argmax, 0)
        self.assertAlmostEqual(p.sum(), 1)
        self.assertTrue(np.isfinite(p).all())
        self.assertGreater(p[0], .99)

    def test_fixed_negatives_exclude_identical_and_ambiguous(self):
        rows = [make_pair(BASE, "T1", BASE["text"] + " "),
                make_pair(BASE, "T6", BASE["text"].replace("on track", "not on track")),
                make_pair(BASE, "T0", BASE["text"]),
                make_pair(BASE, "T9", "The project is on track.")]
        scores = {r["pair_id"]: {"A": s} for r, s in zip(rows, [0.1, 0.9, 10, 10])}
        m = metric(rows, scores, "T6", "A")
        self.assertEqual(m, {"auc": 1.0, "n_positive": 1, "n_negative": 1})

    def test_missing_scores_never_become_zero(self):
        rows = [make_pair(BASE, "T6", "The project is blocked.")]
        self.assertIsNone(metric(rows, {}, "T6", "B768")["auc"])

    def test_constant_scores_are_ties(self):
        rows = [make_pair(BASE, "T1", BASE["text"] + " "), make_pair(BASE, "T6", "The project is blocked.")]
        scores = {r["pair_id"]: {"A": .2} for r in rows}
        self.assertEqual(metric(rows, scores, "T6", "A")["auc"], .5)

    def test_generator_filter_applies_to_both_classes(self):
        rows = [make_pair(BASE, "T1", BASE["text"] + " "),
                make_pair(BASE, "T6", "The project is blocked.", generator="llm")]
        scores = {r["pair_id"]: {"A": .2} for r in rows}
        self.assertIsNone(metric(rows, scores, "T6", "A", "rule")["auc"])

    def test_invalid_ground_truth_rejected(self):
        row = make_pair(BASE, "T9", "Shorter.")
        row["label"] = 1
        with self.assertRaises(ValueError):
            validate_pairs([row])

    def test_duplicate_pair_rejected(self):
        row = make_pair(BASE, "T0", BASE["text"])
        with self.assertRaises(ValueError):
            validate_pairs([row, row])

    def test_rule_edits_do_not_infer_delay_from_date_alone(self):
        rows = generate([BASE])
        self.assertFalse(any(r["category"] in {"T4", "T5"} for r in rows))
        validate_pairs(rows)

    def test_semantic_rule_edits_need_verification(self):
        rows = generate([BASE], [{"base_id": "test", "category": "T6", "strength": "word",
                                  "before": "on track", "after": "blocked"}])
        self.assertFalse(rows[-1]["ground_truth_verified"])

    def test_unknown_model_blocked_before_download(self):
        with self.assertRaises(ValueError):
            verified({"model_id": "unverified/model"})

    def test_fixture_cannot_meet_formal_coverage(self):
        self.assertTrue(coverage(generate([BASE]), [BASE]))

    def test_budget_fuse_prevents_request(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = str(Path(temp) / "ledger.jsonl")
            config = {"verified": True, "model_id": "test-only", "official_source": "test-only",
                      "max_usd_per_million_tokens": 10, "max_usd": 0.000001,
                      "max_output_tokens": 10, "max_calls": 2, "max_total_tokens": 100000}
            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-placeholder"}):
                client = Gemini(config, ledger)
                with patch("urllib.request.urlopen") as network:
                    with self.assertRaisesRegex(RuntimeError, "dollar fuse"):
                        client.request("test", "test")
                    network.assert_not_called()


if __name__ == "__main__":
    unittest.main()

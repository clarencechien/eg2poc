"""Tiny invented data for integration testing ONLY. Never use for hypotheses."""
from src.common import write_jsonl
from src.gen_rule import make_pair


def main():
    bases = []
    pairs = []
    for lang, old in [("en", "The delivery is on track. The deadline is May 31 and shipment is planned for May 10."),
                      ("zh", "交付進度符合計畫。截止日期為五月三十一日，預計五月十日出貨。")]:
        b = {"base_id": f"fixture-{lang}", "doc_id": "invented-fixture", "para_id": 0,
             "lang": lang, "text": old, "source_kind": "test_fixture", "reviewed": False}
        bases.append(b)
        changes = {
            "en": {"T0": old, "T1": old + "  ", "T2": "The deadline is May 31 and shipment is planned for May 10. The delivery is on track.",
                   "T3": "Delivery remains on schedule, with shipment planned for May 10 ahead of the May 31 deadline.",
                   "T4": old.replace("May 10", "May 25"),
                   "T5": "The delivery is delayed. The deadline is May 31 and shipment is now planned for September 30.",
                   "T6": old.replace("is on track", "is not on track"),
                   "T7": old.replace("on track", "behind schedule"),
                   "T8": old + " A new dependency failure now blocks shipment.", "T9": "The deadline is May 31 and shipment is planned for May 10."},
            "zh": {"T0": old, "T1": old + "  ", "T2": "截止日期為五月三十一日，預計五月十日出貨。交付進度符合計畫。",
                   "T3": "目前交付仍按計畫進行，預計在五月三十一日截止前，於五月十日出貨。",
                   "T4": old.replace("五月十日", "五月二十五日"),
                   "T5": "交付進度已延後。截止日期為五月三十一日，目前預計九月三十日出貨。",
                   "T6": old.replace("符合", "不再符合"), "T7": old.replace("符合計畫", "落後計畫"),
                   "T8": old + "新增的相依服務故障目前阻礙出貨。", "T9": "截止日期為五月三十一日，預計五月十日出貨。"}}
        for c, new in changes[lang].items():
            row = make_pair(b, c, new, "sentence", "T6-zh-不再" if c == "T6" and lang == "zh" else None)
            pairs.append(row)
    write_jsonl("tests/fixtures/base.jsonl", bases)
    write_jsonl("tests/fixtures/pairs.jsonl", pairs)


if __name__ == "__main__":
    main()

import argparse
import json
from pathlib import Path
from .common import append_jsonl, read_jsonl, validate_pairs, write_jsonl
from .llm import Gemini, state_judgment


def main():
    p = argparse.ArgumentParser()
    p.add_argument("inputs", nargs="+")
    p.add_argument("--config", default="config.json")
    p.add_argument("--output", default="data/pairs.jsonl")
    p.add_argument("--checks", default="data/checks.jsonl")
    args = p.parse_args()
    rows = [r for path in args.inputs for r in read_jsonl(path) if not r.get("generation_rejected")]
    validate_pairs(rows)
    checks = {r["pair_id"]: r for r in read_jsonl(args.checks)} if Path(args.checks).exists() else {}
    client = None
    accepted = []
    for row in rows:
        if row.get("ground_truth_verified") or row["ambiguous"]:
            accepted.append(row)
            continue
        import hashlib
        fingerprint = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
        check = checks.get(row["pair_id"])
        if check and check.get("fingerprint") != fingerprint:
            raise ValueError("Candidate changed after review; use a new checks ledger")
        if not check:
            client = client or Gemini(json.loads(Path(args.config).read_text())["gemini"])
            judgment = state_judgment(client, row["old_text"], row["new_text"], "independent-check")
            check = {"pair_id": row["pair_id"], "fingerprint": fingerprint,
                     "accepted": judgment["changed"] is not None and int(judgment["changed"]) == row["label"],
                     "judgment": judgment}
            append_jsonl(args.checks, check)
        if check["accepted"]:
            accepted.append(dict(row, ground_truth_verified=True))
    write_jsonl(args.output, accepted)
    print(json.dumps({"candidates": len(rows), "accepted": len(accepted), "rejected": len(rows) - len(accepted)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

import argparse
import importlib.metadata
import json
import random
import time
from pathlib import Path
from .arms import EmbeddingArms, LLMArm, NLIArm, score_a
from .common import append_jsonl, coverage, digest, read_jsonl, validate_pairs, write_jsonl


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pairs", default="data/pairs.jsonl")
    p.add_argument("--base", default="data/base.jsonl")
    p.add_argument("--config", default="config.json")
    p.add_argument("--arms", nargs="+", choices=["A", "B", "C", "D", "E"], default=["A"])
    p.add_argument("--output", default="results/run")
    p.add_argument("--diagnostic", action="store_true", help="Allow fixture data; NEVER interpret as Phase 1 results")
    p.add_argument("--synthetic", action="store_true", help="User-authorized synthetic pilot, not real-document Phase 1")
    args = p.parse_args()
    rows = validate_pairs(read_jsonl(args.pairs))
    if not rows:
        raise ValueError("No pairs: cannot run or report a successful experiment")
    bases = read_jsonl(args.base)
    base_map = {b["base_id"]: b for b in bases}
    if len(base_map) != len(bases):
        raise ValueError("Duplicate base_id")
    for r in rows:
        b = base_map.get(r["base_id"])
        if b is None or b["text"] != r["old_text"] or b["lang"] != r["lang"]:
            raise ValueError("Pair does not match its source base")
    issues = coverage(rows, bases)
    if args.diagnostic and args.synthetic:
        raise ValueError("Choose either diagnostic fixtures or synthetic pilot")
    if not args.diagnostic:
        source = "synthetic_rule" if args.synthetic else "repository"
        if any(not b.get("reviewed") or b.get("source_kind") != source for b in bases):
            raise ValueError("Review real source bases before scoring")
        if any(not r.get("ground_truth_verified") and not r["ambiguous"] for r in rows):
            raise ValueError("Unverified ground truth; run independent check first")
    config = json.loads(Path(args.config).read_text())
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)  # Never overwrite/mix an earlier run.
    packages = {}
    for name in ("numpy", "scikit-learn", "matplotlib", "torch", "transformers", "sentence-transformers"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    manifest = {"diagnostic": args.diagnostic, "synthetic": args.synthetic, "coverage_issues": issues, "packages": packages,
                "pairs_sha256": digest(args.pairs), "base_sha256": digest(args.base), "config_sha256": digest(args.config),
                "config": config, "requested_arms": args.arms, "status": "running", "arm_status": {"B2": "未跑：optional token-level arm"}}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    write_jsonl(out / "pairs.jsonl", rows)
    scores = {r["pair_id"]: {"pair_id": r["pair_id"]} for r in rows}
    def save():
        write_jsonl(out / "scores.jsonl", scores.values())
        (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    try:
        started = time.monotonic()
        if "A" in args.arms:
            for r in rows:
                scores[r["pair_id"]]["A"] = score_a(r["old_text"], r["new_text"])
            manifest["arm_status"]["A"] = "completed"
            save()
            print(f"A completed: {len(rows)} pairs", flush=True)
        if {"B", "C"} & set(args.arms):
            print("Loading EG2 text tower, CPU float32", flush=True)
            embed = EmbeddingArms(config["embedding"], config["labels"])
            backbone = embed.model[0].model
            manifest["embedding_runtime"] = {"class": type(backbone).__name__,
                "parameter_count": sum(p.numel() for p in backbone.parameters()),
                "dtype": str(next(backbone.parameters()).dtype),
                "training": backbone.training,
                "vision_config_disabled": getattr(backbone.config, "vision_config", None) is None,
                "audio_config_disabled": getattr(backbone.config, "audio_config", None) is None}
            print("Measuring repeated T0 noise", flush=True)
            noise = embed.noise(rows, config["seed"])
            write_jsonl(out / "noise.jsonl", noise)
            print("Encoding corpus and both label prefixes", flush=True)
            embed.prepare(rows)
            for r in rows:
                s = scores[r["pair_id"]]
                if "B" in args.arms:
                    s["B768"] = embed.score_b(r["old_text"], r["new_text"])
                    s["B256"] = embed.score_b(r["old_text"], r["new_text"], 256)
                if "C" in args.arms:
                    for prefix in ("classification", "search_query"):
                        value, moved = embed.score_c(r["old_text"], r["new_text"], r["lang"], prefix)
                        s[f"C_{prefix}"], s[f"C_{prefix}_argmax"] = value, moved
            for arm in set(args.arms) & {"B", "C"}:
                manifest["arm_status"][arm] = "completed"
            save()
            print(f"B/C completed after {time.monotonic()-started:.1f}s", flush=True)
        if "D" in args.arms:
            print("Loading three-way multilingual NLI substitute", flush=True)
            nli = NLIArm(config["nli"])
            manifest["nli_runtime"] = {"class": type(nli.model).__name__, "id2label": nli.model.config.id2label,
                "dtype": str(next(nli.model.parameters()).dtype), "training": nli.model.training}
            batch_size = config["nli"]["batch_size"]
            for start in range(0, len(rows), batch_size):
                batch = rows[start:start+batch_size]
                values = nli.score_batch([(r["old_text"], r["new_text"]) for r in batch])
                for r, value in zip(batch, values):
                    scores[r["pair_id"]]["D_NLI"] = value
                    append_jsonl(out / "d-checkpoint.jsonl", scores[r["pair_id"]])
                if start % (batch_size*20) == 0:
                    print(f"D progress: {min(start+batch_size,len(rows))}/{len(rows)}", flush=True)
            manifest["arm_status"]["D"] = "completed: NLI substitute, not Decision Maker"
            save()
        if "E" in args.arms:
            llm = LLMArm(config["gemini"])
            # Fixed seeded round-robin sample over language/category/generator strata.
            rng = random.Random(config["seed"])
            groups = {}
            for r in rows:
                if not r["ambiguous"]:
                    groups.setdefault((r["category"], r["lang"], r["generator"]), []).append(r)
            for group in groups.values():
                rng.shuffle(group)
            sample = []
            while len(sample) < 200 and any(groups.values()):
                for key in sorted(groups):
                    if groups[key] and len(sample) < 200:
                        sample.append(groups[key].pop())
            for r in sample:
                value, reason = llm.score(r["old_text"], r["new_text"])
                scores[r["pair_id"]]["E"] = value
                scores[r["pair_id"]]["E_reason"] = reason
                append_jsonl(out / "e-checkpoint.jsonl", scores[r["pair_id"]])
            manifest["arm_status"]["E"] = f"completed: {len(sample)} sampled judgments; null = abstention"
        manifest["status"] = "completed"
        manifest["elapsed_seconds"] = time.monotonic() - started
    except Exception as exc:
        manifest["status"] = "failed"
        # Exception class only: avoid recording URLs that could contain credentials.
        manifest["error_type"] = type(exc).__name__
        raise
    finally:
        save()


if __name__ == "__main__":
    main()

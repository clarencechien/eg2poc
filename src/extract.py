"""Extract candidates, never silently substitute invented source documents."""
import argparse
import re
import subprocess
from pathlib import Path
from .common import write_jsonl


def main():
    p = argparse.ArgumentParser()
    p.add_argument("repositories", nargs="+")
    p.add_argument("--output", default="data/base-candidates.jsonl")
    args = p.parse_args()
    rows = []
    status = re.compile(r"進度|時程|完成|阻礙|延後|取消|暫停|負責|里程碑|status|progress|deadline|blocked|milestone|deliver|on track|delay", re.I)
    for repo in args.repositories:
        root = Path(repo).resolve()
        commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        paths = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z", "*.md"], text=True).split("\0")
        for rel in filter(None, paths):
            text = subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:{rel}"], text=True)
            text = re.sub(r"```.*?```", "", text, flags=re.S)
            for i, para in enumerate(re.split(r"\n\s*\n", text)):
                para = para.strip()
                if not 80 <= len(para) <= 400 or not status.search(para):
                    continue
                doc = f"{root.name}/{rel}"
                rows.append({"base_id": f"{doc}:{i}", "doc_id": doc, "para_id": i,
                             "lang": "zh" if len(re.findall(r"[\u4e00-\u9fff]", para)) > len(para) / 5 else "en",
                             "text": para, "source_kind": "repository", "source_path": str(root / rel),
                             "source_commit": commit, "reviewed": False})
    write_jsonl(args.output, rows)
    print(f"Extracted {len(rows)} candidates. Review source, language, status content and document balance before copying to data/base.jsonl.")


if __name__ == "__main__":
    main()

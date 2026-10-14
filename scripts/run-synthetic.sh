#!/usr/bin/env bash
set -euo pipefail
cd /workspace/eg2poc
source scripts/env.sh
if [[ $# -ne 1 ]]; then
  echo 'Usage: bash scripts/run-synthetic.sh results/NEW-output-directory' >&2
  exit 2
fi
if [[ ! -e data/synthetic-v1/manifest.json ]]; then
  .venv/bin/python -m src.gen_synthetic
fi
.venv/bin/python -m unittest tests.test_synthetic -v
.venv/bin/python -m src.run --base data/synthetic-v1/base.jsonl \
  --pairs data/synthetic-v1/pairs.jsonl --arms A B C D --synthetic --output "$1"
.venv/bin/python -m src.report "$1"
.venv/bin/python -m src.summarize_synthetic "$1"

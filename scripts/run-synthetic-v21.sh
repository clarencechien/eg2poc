#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
output_dir="${1:-results/synthetic-v2.1}"
.venv/bin/python -m src.report_v2
.venv/bin/python -m unittest tests.test_v21 -v
if [[ ! -f "$output_dir/benchmark-small-models.jsonl" ]]; then
  .venv/bin/python -u -m src.benchmark_v21 --output "$output_dir"
fi
.venv/bin/python -u -m src.run_v21 --model-size e2b --output "$output_dir"
.venv/bin/python -u -m src.run_v21 --model-size e4b --output "$output_dir"
.venv/bin/python -m src.report_v21 --output "$output_dir"

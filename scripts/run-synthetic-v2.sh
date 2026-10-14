#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
if [[ ! -f data/synthetic-v2/manifest.json ]]; then
  .venv/bin/python -m src.gen_synthetic_v2
fi
.venv/bin/python -m unittest tests.test_v2 -v
output_dir="${1:-results/synthetic-v2}"
.venv/bin/python -u -m src.run_v2 --output "$output_dir"
.venv/bin/python -m src.report_v2 --output "$output_dir"

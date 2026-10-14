#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
jevlike_dir="${JEVLIKE_DIR:-/workspace/jevlike}"
llama_dir="${LLAMA_DIR:-/workspace/llama.cpp}"
if [[ ! -d "$jevlike_dir/.git" ]]; then
  git clone https://github.com/clarencechien/jevlike.git "$jevlike_dir"
  git -C "$jevlike_dir" checkout --detach 9838918533cf3d88dc975ef19d38122b07df47f7
fi
[[ "$(git -C "$jevlike_dir" rev-parse HEAD)" == 9838918533cf3d88dc975ef19d38122b07df47f7 ]]
if [[ ! -d "$llama_dir/.git" ]]; then
  git clone --depth 1 --branch b11371 https://github.com/ggml-org/llama.cpp.git "$llama_dir"
fi
[[ "$(git -C "$llama_dir" rev-parse HEAD)" == 99b95488cac0f00ce3f05af113a8c1e287753f87 ]]
.venv/bin/pip install -r requirements-j.txt
.venv/bin/cmake -S "$llama_dir" -B "$llama_dir/build" -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF
.venv/bin/cmake --build "$llama_dir/build" --target llama-server -j 4
.venv/bin/python - <<'PY'
import json
from pathlib import Path
from huggingface_hub import hf_hub_download
plan=json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
for model in plan['models'].values():
    hf_hub_download(model['model_id'],model['file'],revision=model['revision'])
PY

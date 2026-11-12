#!/usr/bin/env bash
# Set up the exploratory D2-DM arm: MediaPipe Decision Maker + EmbeddingGemma 2 text 270M.
# Uses its own venv (.mpvenv) so the pinned torch/transformers stack in .venv is untouched.
set -euo pipefail
cd "$(dirname "$0")/.."

revision=9be6e8b90982095dc05c2bd162e4b954ee4dbac7
expected_sha=2d079ee2f6f066b1f368e8d7c819f55214eaef1d0513b312321901f30ab286fb
model_dir=.cache/models
model="$model_dir/embeddinggemma-2-text-270m.litertlm"

# The mediapipe shared library links libEGL even when only the CPU delegate is used.
if ! ldconfig -p | grep -q 'libEGL.so.1'; then
  if [[ $(id -u) -eq 0 ]]; then
    apt-get install -y -q libegl1 || { apt-get update -q && apt-get install -y -q libegl1; }
  else
    echo "Missing libEGL.so.1: run 'sudo apt-get install libegl1' and retry." >&2
    exit 1
  fi
fi

[[ -x .mpvenv/bin/python ]] || python3 -m venv .mpvenv
.mpvenv/bin/pip install -q mediapipe==1.2.3 requests

mkdir -p "$model_dir"
if [[ ! -f "$model" ]] || [[ "$(sha256sum "$model" | cut -d' ' -f1)" != "$expected_sha" ]]; then
  curl -fsSL -o "$model.part" \
    "https://huggingface.co/litert-community/embeddinggemma-2-text-270m-litert-lm/resolve/$revision/embeddinggemma-2-text-270m.litertlm"
  mv "$model.part" "$model"
fi
[[ "$(sha256sum "$model" | cut -d' ' -f1)" == "$expected_sha" ]] || { echo "Model SHA256 mismatch" >&2; exit 1; }
.mpvenv/bin/python -c "import mediapipe as mp; assert mp.__version__ == '1.2.3'; mp.tasks.decision.DecisionMaker.create_from_model_path('$model').close(); print('mediapipe', mp.__version__, 'OK:', '$model')" 2>&1 | grep -E 'OK:|Error|error' || true

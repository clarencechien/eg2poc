#!/usr/bin/env bash
# Set up the exploratory D2-DM arms: MediaPipe Decision Maker with EG2 / Laya / GLiNER backends.
# Uses its own venv (.mpvenv) so the pinned torch/transformers stack in .venv is untouched.
# Usage: bash scripts/setup-mp-decision.sh [eg2] [laya] [gliner]   (default: all three)
set -euo pipefail
cd "$(dirname "$0")/.."

declare -A url sha
url[eg2]=https://huggingface.co/litert-community/embeddinggemma-2-text-270m-litert-lm/resolve/9be6e8b90982095dc05c2bd162e4b954ee4dbac7/embeddinggemma-2-text-270m.litertlm
sha[eg2]=2d079ee2f6f066b1f368e8d7c819f55214eaef1d0513b312321901f30ab286fb
# Google's Decision Maker bucket only serves "latest"; the SHA256 pins the 2026-11-12 object
# (Laya generation 1791232006884043, GLiNER generation 1791242707069212). A mismatch means
# Google replaced the file: record the new hash as a new version instead of editing results.
url[laya]=https://storage.googleapis.com/mediapipe-models/decision_maker/laya/float32/laya_s512/latest/laya_s512.task
sha[laya]=e9f1693861c9a79a541d6f716648142ee844fd2e7119c9ed48d166f4b85a15df
url[gliner]=https://storage.googleapis.com/mediapipe-models/decision_maker/gliner/float16/gliner_s512/latest/gliner_s512.task
sha[gliner]=23a02e1b286fab7573ef2a00acbd8bf80fd2b1284de25eb8fafcd74f8bccd7ec

backends=("$@"); [[ ${#backends[@]} -gt 0 ]] || backends=(eg2 laya gliner)
model_dir=.cache/models

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
for b in "${backends[@]}"; do
  [[ -n "${url[$b]:-}" ]] || { echo "Unknown backend: $b" >&2; exit 1; }
  model="$model_dir/$(basename "${url[$b]}")"
  if [[ ! -f "$model" ]] || [[ "$(sha256sum "$model" | cut -d' ' -f1)" != "${sha[$b]}" ]]; then
    curl -fsSL -o "$model.part" "${url[$b]}"
    mv "$model.part" "$model"
  fi
  [[ "$(sha256sum "$model" | cut -d' ' -f1)" == "${sha[$b]}" ]] || { echo "$b: model SHA256 mismatch ($model)" >&2; exit 1; }
  echo "$b OK: $model"
done
.mpvenv/bin/python -c "import mediapipe as mp; assert mp.__version__ == '1.2.3'; print('mediapipe', mp.__version__)"

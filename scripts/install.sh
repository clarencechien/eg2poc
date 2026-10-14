#!/usr/bin/env bash
set -euo pipefail
cd /workspace/eg2poc
source scripts/env.sh
if [[ ! -x .venv/bin/python ]]; then
  python -m venv .venv
fi
.venv/bin/python -m pip install 'torch==2.14.1+cpu' 'torchvision==0.29.1+cpu' --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v

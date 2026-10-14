# Source from bash. Keep all writable caches inside the checkout's ignored paths.
export HF_HOME="${HF_HOME:-/workspace/eg2poc/.cache/huggingface}"
export HF_HUB_DISABLE_XET=1
export HF_HUB_DISABLE_PROGRESS_BARS=1
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/workspace/eg2poc/.cache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/workspace/eg2poc/.cache/matplotlib}"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-/workspace/eg2poc/.cache/pip}"
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=false

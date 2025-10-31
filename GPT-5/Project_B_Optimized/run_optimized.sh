#!/usr/bin/env bash
set -euo pipefail
if [ ! -d .venv_optimized ]; then
  bash setup_optimized.sh
else
  source .venv_optimized/bin/activate || source .venv_optimized/Scripts/activate
fi
python test_optimized.py

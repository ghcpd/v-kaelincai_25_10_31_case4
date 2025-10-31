#!/usr/bin/env bash
set -euo pipefail
if [ ! -d .venv_original ]; then
  bash setup_original.sh
else
  source .venv_original/bin/activate || source .venv_original/Scripts/activate
fi
python test_original.py

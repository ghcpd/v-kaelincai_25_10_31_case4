#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv_optimized
source .venv_optimized/bin/activate || source .venv_optimized/Scripts/activate
pip install --upgrade pip
pip install -r requirements_optimized.txt
echo "Optimized environment setup complete."

#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv_original
source .venv_original/bin/activate || source .venv_original/Scripts/activate
pip install --upgrade pip
pip install -r requirements_original.txt
echo "Faulty environment setup complete."

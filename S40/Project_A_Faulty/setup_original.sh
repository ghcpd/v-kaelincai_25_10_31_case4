#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv_faulty
source .venv_faulty/bin/activate
pip install --upgrade pip
pip install -r requirements_original.txt

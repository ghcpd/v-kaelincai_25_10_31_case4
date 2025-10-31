#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv_original
source .venv_original/bin/activate
pip install --upgrade pip
pip install -r requirements_original.txt

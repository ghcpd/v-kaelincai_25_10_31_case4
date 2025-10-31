#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

if [ -f ".venv/Scripts/activate" ]; then
  # Windows virtual environment activation.
  source ".venv/Scripts/activate"
else
  source ".venv/bin/activate"
fi

pip install --upgrade pip
pip install -r requirements_original.txt

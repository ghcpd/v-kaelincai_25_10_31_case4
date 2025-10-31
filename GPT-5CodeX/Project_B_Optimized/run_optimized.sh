#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
  ./setup_optimized.sh
fi

if [ -f ".venv/Scripts/activate" ]; then
  source ".venv/Scripts/activate"
else
  source ".venv/bin/activate"
fi

RUNS=${RUNS:-30}
LOG_FILE="log_optimized.txt"
TIME_FILE="time_optimized.txt"
RESULTS_FILE="results_optimized.json"

: > "$LOG_FILE"
: > "$TIME_FILE"

python test_optimized.py --runs "$RUNS" --log "$LOG_FILE" --time "$TIME_FILE" --results "$RESULTS_FILE"

python - <<'PYCODE'
from pathlib import Path
import json

results = Path('results_optimized.json')
if results.exists():
    payload = json.loads(results.read_text(encoding='utf-8'))
    print(f"[optimized] Stability rate: {payload['aggregate']['stability_rate'] * 100:.1f}%")
PYCODE

if [ -n "${VIRTUAL_ENV:-}" ]; then
  deactivate
fi

#!/usr/bin/env bash
set -euo pipefail
if [ -d .venv_optimized ]; then
  source .venv_optimized/bin/activate
fi
pytest -q --maxfail=1 --disable-warnings --count 3 | tee log_optimized.txt
/usr/bin/time -v python -m pytest -q --maxfail=1 --disable-warnings --count 3 > time_optimized.txt 2>&1 || true
python -m pytest -q --maxfail=1 --disable-warnings --count 10 --json-report --json-report-file results_optimized.json > /dev/null 2>&1 || true

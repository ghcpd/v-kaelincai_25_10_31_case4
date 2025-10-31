#!/usr/bin/env bash
set -euo pipefail
if [ -d .venv_faulty ]; then
	source .venv_faulty/bin/activate
fi
pytest -q --maxfail=1 --disable-warnings --reruns 3 --reruns-delay 0.1 --count 3 | tee log_original.txt
/usr/bin/time -v python -m pytest -q --maxfail=1 --disable-warnings --reruns 3 --reruns-delay 0.1 --count 3 > time_original.txt 2>&1 || true
python -m pytest -q --maxfail=1 --disable-warnings --reruns 3 --reruns-delay 0.1 --count 5 --json-report --json-report-file results_original.json > /dev/null 2>&1 || true

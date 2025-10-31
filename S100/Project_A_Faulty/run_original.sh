#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv_original" ]; then
  echo "[setup] creating virtual environment"
  python -m venv .venv_original
fi
source .venv_original/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements_original.txt >/dev/null

# repeat pytest runs to capture flakiness
runs=${1:-20}
log_file="log_original.txt"
time_file="time_original.txt"
results_json="results_original.json"

rm -f "$log_file" "$time_file" "$results_json"

echo "{" >"$results_json"
echo "  \"runs\": $runs," >>"$results_json"
echo "  \"failures\": [" >>"$results_json"

for i in $(seq 1 $runs); do
  start=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)
  echo "[run $i] starting" | tee -a "$log_file"
  if pytest -q --disable-warnings >>"$log_file" 2>&1; then
    status="pass"
  else
    status="fail"
  fi
  end=$(python - <<'PY'
import time
print(time.perf_counter())
PY
)
  elapsed=$(python - <<'PY'
import sys
start=float(sys.argv[1])
end=float(sys.argv[2])
print(f"{end-start:.5f}")
PY
"$start" "$end")
  echo "$elapsed" >>"$time_file"
  echo "    {\"run\": $i, \"status\": \"$status\"}," >>"$results_json"
  sleep 0.1
 done

echo "  ]" >>"$results_json"
# placeholder aggregated metrics computed later
python - <<'PY'
import json
from pathlib import Path
import numpy as np

time_values = []
if Path("time_original.txt").exists():
    with open("time_original.txt") as fh:
        time_values = [float(line.strip()) for line in fh if line.strip()]

data = {
    "avg_time": float(np.mean(time_values)) if time_values else None,
    "std_time": float(np.std(time_values)) if time_values else None,
    "variance": float(np.var(time_values)) if time_values else None,
}
print(json.dumps(data))
Path("results_original.json").write_text(
    Path("results_original.json").read_text().rstrip(",\n") + ",\n  \"timing\": " + json.dumps(data) + "\n}\n"
)
PY

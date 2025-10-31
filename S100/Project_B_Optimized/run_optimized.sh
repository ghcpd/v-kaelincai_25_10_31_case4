#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv_optimized" ]; then
  echo "[setup] creating virtual environment"
  python -m venv .venv_optimized
fi
source .venv_optimized/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements_optimized.txt >/dev/null

runs=${1:-20}
log_file="log_optimized.txt"
time_file="time_optimized.txt"
results_json="results_optimized.json"

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
 done

echo "  ]" >>"$results_json"
python - <<'PY'
import json
from pathlib import Path
import numpy as np

time_values = []
if Path("time_optimized.txt").exists():
    with open("time_optimized.txt") as fh:
        time_values = [float(line.strip()) for line in fh if line.strip()]

data = {
    "avg_time": float(np.mean(time_values)) if time_values else None,
    "std_time": float(np.std(time_values)) if time_values else None,
    "variance": float(np.var(time_values)) if time_values else None,
}
Path("results_optimized.json").write_text(
    Path("results_optimized.json").read_text().rstrip(",\n") + ",\n  \"timing\": " + json.dumps(data) + "\n}\n"
)
print(json.dumps(data))
PY

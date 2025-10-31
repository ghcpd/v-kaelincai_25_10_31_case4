#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT_DIR"

if [ -f Project_A_Faulty/setup_original.sh ]; then
  bash Project_A_Faulty/setup_original.sh
fi
if [ -f Project_B_Optimized/setup_optimized.sh ]; then
  bash Project_B_Optimized/setup_optimized.sh
fi

cd Project_A_Faulty
bash run_original.sh || true
cd ..

cd Project_B_Optimized
bash run_optimized.sh || true
cd ..

python - <<'PY'
import json
from pathlib import Path

root = Path(__file__).parent
report_path = root / "compare_report.md"

metrics = {
    "A": {
        "results": root / "Project_A_Faulty" / "results_original.json",
        "time": root / "Project_A_Faulty" / "time_original.txt",
        "log": root / "Project_A_Faulty" / "log_original.txt",
    },
    "B": {
        "results": root / "Project_B_Optimized" / "results_optimized.json",
        "time": root / "Project_B_Optimized" / "time_optimized.txt",
        "log": root / "Project_B_Optimized" / "log_optimized.txt",
    },
}

summary = {}
for key, data in metrics.items():
    summary[key] = {}
    if data["results"].exists():
        try:
            content = data["results"].read_text(encoding="utf-8")
            summary[key]["results"] = content
        except Exception:
            summary[key]["results"] = ""
    if data["time"].exists():
        summary[key]["time"] = data["time"].read_text(encoding="utf-8")
    if data["log"].exists():
        summary[key]["log"] = data["log"].read_text(encoding="utf-8")

report_lines = report_path.read_text(encoding="utf-8").splitlines()
for idx, line in enumerate(report_lines):
    if "TODO" in line:
        if "Project A" in line:
            report_lines[idx] = line.replace("TODO", "TBD")
        elif "Project B" in line:
            report_lines[idx] = line.replace("TODO", "TBD")
report_path.write_text("\n".join(report_lines), encoding="utf-8")

(root / "aggregate_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
PY

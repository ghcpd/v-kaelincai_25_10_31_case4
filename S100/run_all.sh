#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)

pushd "$ROOT/Project_A_Faulty" >/dev/null
bash run_original.sh ${1:-20}
popd >/dev/null

pushd "$ROOT/Project_B_Optimized" >/dev/null
bash run_optimized.sh ${1:-20}
popd >/dev/null

python - <<'PY'
import json
from pathlib import Path
import numpy as np

root = Path('.').resolve()

orig = json.loads((root / 'Project_A_Faulty' / 'results_original.json').read_text())
opt = json.loads((root / 'Project_B_Optimized' / 'results_optimized.json').read_text())

report_path = root / 'compare_report.md'
content = report_path.read_text()

stability_a = 100 - (sum(1 for r in orig['failures'] if r['status'] == 'fail') / max(orig['runs'], 1) * 100)
stability_b = 100 - (sum(1 for r in opt['failures'] if r['status'] == 'fail') / max(opt['runs'], 1) * 100)

def format_float(value):
    if value is None:
        return 'n/a'
    return f"{value:.5f}"

replacements = {
    'Stability rate (% consistent runs) | TBD | TBD | TBD': f"Stability rate (% consistent runs) | {stability_a:.2f} | {stability_b:.2f} | {stability_b - stability_a:.2f}",
    'Average runtime (s) | TBD | TBD | TBD': f"Average runtime (s) | {format_float(orig['timing'].get('avg_time'))} | {format_float(opt['timing'].get('avg_time'))} | {format_float((opt['timing'].get('avg_time') or 0) - (orig['timing'].get('avg_time') or 0))}",
    'Runtime stddev (s) | TBD | TBD | TBD': f"Runtime stddev (s) | {format_float(orig['timing'].get('std_time'))} | {format_float(opt['timing'].get('std_time'))} | {format_float((opt['timing'].get('std_time') or 0) - (orig['timing'].get('std_time') or 0))}",
    'Failure count | TBD | TBD | TBD': f"Failure count | {sum(1 for r in orig['failures'] if r['status'] == 'fail')} | {sum(1 for r in opt['failures'] if r['status'] == 'fail')} | {(sum(1 for r in opt['failures'] if r['status'] == 'fail')) - (sum(1 for r in orig['failures'] if r['status'] == 'fail'))}",
}

for placeholder, replacement in replacements.items():
    content = content.replace(placeholder, replacement)

report_path.write_text(content)

summary = {
    'stability_a': stability_a,
    'stability_b': stability_b,
    'avg_time_a': orig['timing'].get('avg_time'),
    'avg_time_b': opt['timing'].get('avg_time'),
    'std_time_a': orig['timing'].get('std_time'),
    'std_time_b': opt['timing'].get('std_time'),
    'runs': {'project_a': orig['runs'], 'project_b': opt['runs']},
}

(Path('aggregate_results.json')).write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY

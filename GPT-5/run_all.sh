#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(pwd)

echo "Running Project A (Faulty)"\n
pushd Project_A_Faulty >/dev/null
bash run_original.sh
popd >/dev/null

echo "Running Project B (Optimized)"\n
pushd Project_B_Optimized >/dev/null
bash run_optimized.sh
popd >/dev/null

python - <<'PYCODE'
import json, os, statistics
root = os.getcwd()
res_a = json.load(open(os.path.join(root, 'Project_A_Faulty', 'results_original.json')))
res_b = json.load(open(os.path.join(root, 'Project_B_Optimized', 'results_optimized.json')))

def index_by_case(data):
    return {r['case_id']: r for r in data['runs']}
A = index_by_case(res_a)
B = index_by_case(res_b)
lines = []
lines.append('# Comparison Report')
lines.append('\n| Case | Orig Stability | Opt Stability | Orig Unique | Opt Unique | Orig Failures | Opt Failures | Avg Time Orig (ms) | Avg Time Opt (ms) |')
lines.append('|------|---------------:|-------------:|-----------:|----------:|--------------:|-------------:|-------------------:|------------------:|')
for cid in A:
    a = A[cid]; b = B.get(cid, {})
    lines.append(f"| {cid} | {a.get('stability_rate',0):.2f} | {b.get('stability_rate',0):.2f} | {a.get('observed_unique_results',0)} | {b.get('observed_unique_results',0)} | {a.get('failures',0)} | {b.get('failures',0)} | {a.get('avg_runtime_sec',0)*1000:.2f} | {b.get('avg_runtime_sec',0)*1000:.2f} |")
lines.append('\n## Mitigation Strategies Applied')
lines.append('- Removed time-dependent modulo skip logic.')
lines.append('- Added deterministic random seed.')
lines.append('- Introduced retry with backoff for transient errors.')
lines.append('- Eliminated shared global mutable accumulation.')
lines.append('- Added validation for non-numeric inputs.')
lines.append('\n## Residual Nondeterminism')
lines.append('Optimized version should be fully deterministic given fixed seed; any residual variance would stem from OS scheduling variation in timing (not affecting results).')
open('compare_report.md','w',encoding='utf-8').write('\n'.join(lines))
print('compare_report.md generated.')
PYCODE

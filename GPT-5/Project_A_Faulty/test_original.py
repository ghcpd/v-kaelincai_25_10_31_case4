"""Test harness to expose flaky behavior in original implementation.
Runs each test case multiple times and records stability metrics.
Generates: results_original.json, log_original.txt, time_original.txt
"""
from __future__ import annotations
import json, os, statistics, time
from typing import Any, Dict, List

import original_code  # type: ignore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DATA_PATH = os.path.join(ROOT, 'test_data.json')
OUT_DIR = os.path.dirname(__file__)
N_RUNS = 15

RESULTS: List[Dict[str, Any]] = []
LOG_LINES: List[str] = []
TIMING_LINES: List[str] = []

with open(TEST_DATA_PATH, 'r', encoding='utf-8') as f:
    test_cases = json.load(f)["cases"]

for case in test_cases:
    case_id = case["id"]
    expected = case.get("expected_result")
    variance_threshold = case.get("variance_threshold", 0)
    expect_failure = case.get("expect_failure", False)
    sums: List[int] = []
    durations: List[float] = []
    failures = 0
    for i in range(N_RUNS):
        t0 = time.perf_counter()
        try:
            res = original_code.process_case(case)
            reported = res["reported_sum"]
            sums.append(reported)
            durations.append(res["duration_sec"])
            LOG_LINES.append(f"CASE {case_id} RUN {i} => sum={reported} drops={res['drop_count']} duration={res['duration_sec']:.5f}")
        except Exception as e:
            failures += 1
            LOG_LINES.append(f"CASE {case_id} RUN {i} EXCEPTION {e}")
        TIMING_LINES.append(f"{case_id},run={i},{durations[-1] if durations else 'NA'}")
    unique_results = len(set(sums))
    stability_rate = 0.0
    if expected is not None and sums:
        matches = sum(1 for s in sums if (s == expected or (variance_threshold and abs(s-expected) <= variance_threshold)))
        stability_rate = matches / N_RUNS
    elif not sums:
        stability_rate = 0.0
    avg_runtime = statistics.mean(durations) if durations else 0.0
    std_runtime = statistics.pstdev(durations) if len(durations) > 1 else 0.0
    RESULTS.append({
        "case_id": case_id,
        "expected": expected,
        "observed_unique_results": unique_results,
        "stability_rate": stability_rate,
        "failures": failures,
        "avg_runtime_sec": avg_runtime,
        "std_runtime_sec": std_runtime,
        "all_results": sums[:10]  # sample
    })

# Write artifacts
with open(os.path.join(OUT_DIR, 'results_original.json'), 'w', encoding='utf-8') as f:
    json.dump({"runs": RESULTS, "total_cases": len(RESULTS)}, f, indent=2)
with open(os.path.join(OUT_DIR, 'log_original.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(LOG_LINES))
with open(os.path.join(OUT_DIR, 'time_original.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(TIMING_LINES))

print("Original flaky test execution complete. See results_original.json and log_original.txt")

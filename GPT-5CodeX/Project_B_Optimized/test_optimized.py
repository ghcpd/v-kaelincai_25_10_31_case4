#!/usr/bin/env python3
"""Repeated-run harness validating the hardened implementation."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from optimized_code import OrderValidationError, load_orders, process_orders, reset_state

PROJECT_ROOT = Path(__file__).parent
TEST_DATA_PATH = PROJECT_ROOT / "test_data.json"
INPUT_DATA_PATH = PROJECT_ROOT / "input_data.json"


def deterministic_total(orders: Iterable[dict]) -> float:
    total = 0.0
    for order in orders:
        total += float(order["quantity"]) * float(order["unit_price"])
    return round(total, 2)


def load_test_cases() -> List[Dict[str, Any]]:
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _case_one(expected_total: float) -> Tuple[bool, Dict[str, Any]]:
    reset_state()
    result = process_orders()
    observed = round(result["total_revenue"], 2)
    passed = math.isclose(observed, expected_total, rel_tol=0.0, abs_tol=0.0)
    return passed, {"observed": observed, "expected": expected_total, "details": result}


def _case_two(case: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    reset_state()
    cfg = case["input"]
    result = process_orders(
        synthetic_orders=cfg["synthetic_orders"],
        quantity_range=cfg["quantity_range"],
        price_range=cfg["price_range"],
    )
    observed = round(result["total_revenue"], 2)
    expected = round(case["expected"]["total_revenue"], 2)
    passed = math.isclose(observed, expected, rel_tol=0.0, abs_tol=0.0)
    return passed, {"observed": observed, "expected": expected, "details": result}


def _case_three(case: Dict[str, Any], baseline_orders: List[dict], baseline_total: float) -> Tuple[bool, Dict[str, Any]]:
    reset_state()
    orders = baseline_orders + case["input"]["orders"]
    result = process_orders(orders=orders)
    observed = round(result["total_revenue"], 2)
    passed = math.isclose(observed, baseline_total, rel_tol=0.0, abs_tol=0.0)
    return passed, {"observed": observed, "expected": baseline_total, "details": result}


def _case_four(case: Dict[str, Any], baseline_orders: List[dict]) -> Tuple[bool, Dict[str, Any]]:
    reset_state()
    orders = baseline_orders + case["input"]["orders"]
    try:
        process_orders(orders=orders)
    except OrderValidationError as exc:
        return True, {"exception": str(exc)}
    return False, {"exception": None, "details": "Expected OrderValidationError"}


def _case_five(case: Dict[str, Any], baseline_orders: List[dict]) -> Tuple[bool, Dict[str, Any]]:
    reset_state()
    result = process_orders(orders=baseline_orders, timestamp_override=case["input"]["timestamp_override"])
    observed = bool(result.get("discount_active"))
    expected = bool(case["expected"]["discount_applied"])
    passed = observed is expected
    return passed, {"observed": observed, "expected": expected, "details": result}


def run_suite(run_id: int, cases: List[Dict[str, Any]], log_handle) -> Dict[str, Any]:
    baseline_orders = load_orders(INPUT_DATA_PATH)
    baseline_total = deterministic_total(baseline_orders)

    case_dispatch = {
        "case_01": lambda case: _case_one(baseline_total),
        "case_02": _case_two,
        "case_03": lambda case: _case_three(case, baseline_orders, baseline_total),
        "case_04": lambda case: _case_four(case, baseline_orders),
        "case_05": lambda case: _case_five(case, baseline_orders),
    }

    run_results: List[Dict[str, Any]] = []
    run_start = time.perf_counter()

    for case in cases:
        case_id = case["id"]
        start = time.perf_counter()
        handler = case_dispatch[case_id]
        passed, payload = handler(case)
        duration = time.perf_counter() - start
        run_results.append(
            {
                "case_id": case_id,
                "passed": passed,
                "duration_sec": duration,
                "payload": payload,
            }
        )

    run_duration = time.perf_counter() - run_start

    summary = {
        "run": run_id,
        "failures": sum(1 for case in run_results if not case["passed"]),
        "cases": run_results,
        "duration_sec": run_duration,
    }
    log_handle.write(json.dumps(summary) + "\n")
    log_handle.flush()
    return summary


def aggregate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    durations = [entry["duration_sec"] for entry in results]
    failure_counts = [entry["failures"] for entry in results]
    total_runs = len(results)
    stable_runs = sum(1 for fail in failure_counts if fail == 0)

    case_stats: Dict[str, Dict[str, Any]] = {}
    for entry in results:
        for case in entry["cases"]:
            bucket = case_stats.setdefault(case["case_id"], {"runs": 0, "failures": 0, "durations": []})
            bucket["runs"] += 1
            bucket["durations"].append(case["duration_sec"])
            if not case["passed"]:
                bucket["failures"] += 1

    def durability(bucket: Dict[str, Any]) -> Dict[str, Any]:
        durations = bucket["durations"]
        return {
            "runs": bucket["runs"],
            "failures": bucket["failures"],
            "stability_rate": round(1 - (bucket["failures"] / max(bucket["runs"], 1)), 3),
            "avg_duration": statistics.mean(durations) if durations else 0.0,
            "duration_stddev": statistics.pstdev(durations) if len(durations) > 1 else 0.0,
        }

    return {
        "total_runs": total_runs,
        "stable_runs": stable_runs,
        "stability_rate": round(stable_runs / max(total_runs, 1), 3),
        "avg_duration": statistics.mean(durations) if durations else 0.0,
        "duration_stddev": statistics.pstdev(durations) if len(durations) > 1 else 0.0,
        "case_metrics": {case_id: durability(bucket) for case_id, bucket in case_stats.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stability tests against optimized implementation.")
    parser.add_argument("--runs", type=int, default=30, help="Number of times to execute the suite")
    parser.add_argument("--log", type=Path, default=Path("log_optimized.txt"), help="Log file path")
    parser.add_argument("--time", type=Path, default=Path("time_optimized.txt"), help="Timing output path")
    parser.add_argument(
        "--results", type=Path, default=Path("results_optimized.json"), help="Structured results JSON path"
    )
    args = parser.parse_args()

    cases = load_test_cases()
    results: List[Dict[str, Any]] = []

    with open(args.log, "a", encoding="utf-8") as log_handle:
        for run_idx in range(1, args.runs + 1):
            results.append(run_suite(run_idx, cases, log_handle))

    metrics = aggregate_metrics(results)

    with open(args.results, "w", encoding="utf-8") as handle:
        json.dump({"runs": results, "aggregate": metrics}, handle, indent=2)

    with open(args.time, "w", encoding="utf-8") as handle:
        handle.write("run,duration_sec,failures\n")
        for entry in results:
            handle.write(f"{entry['run']},{entry['duration_sec']:.6f},{entry['failures']}\n")
        handle.write(
            f"aggregate,{metrics['avg_duration']:.6f},{len(results) - metrics['stable_runs']}\n"
        )


if __name__ == "__main__":
    main()

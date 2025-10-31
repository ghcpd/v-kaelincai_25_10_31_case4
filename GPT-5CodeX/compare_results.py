#!/usr/bin/env python3
"""Generate comparison report between faulty and optimized implementations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

ROOT = Path(__file__).parent
PROJECT_A = ROOT / "Project_A_Faulty" / "results_original.json"
PROJECT_B = ROOT / "Project_B_Optimized" / "results_optimized.json"
REPORT_PATH = ROOT / "compare_report.md"


def load_results(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing results file: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_case_ids(payload: Dict[str, object]) -> Iterable[str]:
    return payload["aggregate"]["case_metrics"].keys()


def render_table(a_cases: Dict[str, dict], b_cases: Dict[str, dict]) -> str:
    headers = [
        "Case",
        "A Stability",
        "B Stability",
        "A Avg (s)",
        "B Avg (s)",
        "A Failures",
        "B Failures",
    ]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    case_ids = sorted(set(a_cases) | set(b_cases))
    for case_id in case_ids:
        a = a_cases.get(case_id, {})
        b = b_cases.get(case_id, {})
        line = "| {case} | {a_stab:.1%} | {b_stab:.1%} | {a_avg:.4f} | {b_avg:.4f} | {a_fail} | {b_fail} |".format(
            case=case_id,
            a_stab=a.get("stability_rate", 0.0),
            b_stab=b.get("stability_rate", 0.0),
            a_avg=a.get("avg_duration", 0.0),
            b_avg=b.get("avg_duration", 0.0),
            a_fail=a.get("failures", 0),
            b_fail=b.get("failures", 0),
        )
        lines.append(line)
    return "\n".join(lines)


def describe_strategies() -> str:
    return (
        "- Introduced deterministic synthetic order generation and Decimal rounding to remove floating jitter.\n"
        "- Removed shared mutable state, performing aggregation on the main thread with executor coordination.\n"
        "- Implemented strict validation and structured exceptions to ensure malformed inputs fail fast.\n"
        "- Normalised time-based discount logic with explicit parsing and deterministic evaluation.\n"
        "- Added high-volume repeated-run harness with structured metrics for reproducibility."
    )


def describe_residual() -> str:
    return (
        "- Performance measurements are taken on the local machine and may still fluctuate due to system load.\n"
        "- External integrations (e.g., real payment gateways) are mocked; additional contract tests are recommended.\n"
        "- Long-running workloads may benefit from adaptive batch sizing or async IO to further reduce latency variance."
    )


def build_report(a_payload: Dict[str, object], b_payload: Dict[str, object]) -> str:
    a_agg = a_payload["aggregate"]
    b_agg = b_payload["aggregate"]

    table = render_table(a_agg["case_metrics"], b_agg["case_metrics"])

    report = f"""# Comparison Report

## Aggregate Stability
- Project A (Faulty): {a_agg['stable_runs']} / {a_agg['total_runs']} runs stable ({a_agg['stability_rate']:.1%})
- Project B (Optimized): {b_agg['stable_runs']} / {b_agg['total_runs']} runs stable ({b_agg['stability_rate']:.1%})
- Average runtime delta: {a_agg['avg_duration'] - b_agg['avg_duration']:+.4f} seconds per run

## Per-Test Metrics
{table}

## Mitigation Strategies
{describe_strategies()}

## Residual Risks & Next Steps
{describe_residual()}
"""
    return report


def main() -> None:
    payload_a = load_results(PROJECT_A)
    payload_b = load_results(PROJECT_B)
    report = build_report(payload_a, payload_b)
    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()

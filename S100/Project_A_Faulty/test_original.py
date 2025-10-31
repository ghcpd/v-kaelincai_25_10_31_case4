"""Automated tests intentionally built to expose flaky behavior.

The harness runs repeated invocations to demonstrate nondeterministic
outputs. We expect occasional assertion failures, demonstrating the
existing instability.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

from original_code import process_file, score_batch

ROOT = Path(__file__).parent
TEST_DATA = json.loads((ROOT / "test_data.json").read_text())


def _run_multiple(times: int, func, *args, **kwargs) -> List[Any]:
    results = []
    for _ in range(times):
        results.append(func(*args, **kwargs))
    return results


def test_baseline_is_inconsistent():
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "baseline_deterministic")
    payload = case["input"]
    results = _run_multiple(10, score_batch, payload["transactions"])
    totals = {round(result["total_score"], 2) for result in results}
    assert len(totals) > 1, "Expected inconsistent total scores but found deterministic behavior"


def test_concurrent_updates_show_race():
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "concurrency_race")
    payload = case["input"]

    outputs: List[Dict[str, Any]] = []

    def worker():
        outputs.append(score_batch(payload["transactions"]))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    trending_orders = {tuple(result["trending_ids"]) for result in outputs}
    assert len(trending_orders) > 1, "Expected race condition to alter order of trending IDs"


def test_state_leakage_detected(tmp_path):
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "state_leakage")
    payload = case["input"]

    first = score_batch(payload["transactions"])
    second = score_batch(payload["transactions"])

    assert first["total_score"] != second["total_score"], "Global state should leak across runs"


def test_malformed_payload_not_consistent():
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "malformed_payload")
    payload = case["input"]

    with pytest.raises(Exception):
        score_batch(payload["transactions"])


def test_process_file_runs_multiple_times(tmp_path):
    temp_file = tmp_path / "payload.json"
    temp_file.write_text(json.dumps({"transactions": []}))
    results = _run_multiple(5, process_file, temp_file)
    totals = [result["summary"]["wall_clock_factor"] for result in results]
    assert np.std(totals) > 0.1, "Wall clock jitter should introduce variance"

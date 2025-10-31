import json
import time
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent
CODE_PATH = PROJECT_ROOT / "original_code.py"
INPUT_PATH = PROJECT_ROOT / "input_data.json"


def _run_process_orders() -> subprocess.CompletedProcess:
    return subprocess.run([
        sys.executable,
        str(CODE_PATH),
    ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _validate_json(payload: str) -> None:
    data = json.loads(payload)
    assert isinstance(data, list)
    assert len(data) >= 1
    for entry in data:
        assert "id" in entry
        assert "shipping_cost" in entry
        assert "discounted_amount" in entry


@pytest.mark.flaky(reruns=5)
def test_process_orders_exhibits_flakiness():
    """Repeated runs should reveal intermittent failures."""
    proc = _run_process_orders()
    if proc.returncode != 0:
        pytest.fail(f"Process failed: {proc.stderr}")
    _validate_json(proc.stdout)


def test_consistency_across_runs():
    outputs = []
    for _ in range(5):
        proc = _run_process_orders()
        outputs.append(proc.stdout)
        time.sleep(0.05)
    assert len(set(outputs)) > 1, "Expected nondeterministic outputs"


def test_error_injection_detected():
    failures = 0
    for _ in range(10):
        proc = _run_process_orders()
        if proc.returncode != 0:
            failures += 1
    assert failures >= 1, "Expected at least one simulated downstream failure"

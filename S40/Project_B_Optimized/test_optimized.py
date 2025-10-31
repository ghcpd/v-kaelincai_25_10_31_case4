import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent
CODE_PATH = PROJECT_ROOT / "optimized_code.py"
INPUT_PATH = PROJECT_ROOT / "input_data.json"


def _run_process_orders() -> subprocess.CompletedProcess:
    return subprocess.run([
        sys.executable,
        str(CODE_PATH),
    ],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


def _load_output() -> list[dict]:
    proc = _run_process_orders()
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_outputs_are_deterministic():
    first = _load_output()
    second = _load_output()
    assert first == second


def test_expected_fields_present():
    data = _load_output()
    for entry in data:
        assert set(entry) == {"id", "shipping_cost", "discounted_amount", "region", "timestamp"}
        assert entry["timestamp"] == 0.0


def test_stress_repeat_consistency():
    outputs = [tuple(sorted((item["id"], item["shipping_cost"]) for item in _load_output())) for _ in range(10)]
    assert len(set(outputs)) == 1


def test_validation_against_schema():
    from jsonschema import validate  # type: ignore

    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["id", "shipping_cost", "discounted_amount", "region", "timestamp"],
            "properties": {
                "id": {"type": "string"},
                "shipping_cost": {"type": "number"},
                "discounted_amount": {"type": "number"},
                "region": {"type": "string"},
                "timestamp": {"type": "number"},
            },
        },
    }
    validate(instance=_load_output(), schema=schema)


def test_performance_benchmark(benchmark):
    data_path = INPUT_PATH
    from optimized_code import process_orders  # type: ignore

    def run():
        return process_orders(data_path)

    result = benchmark(run)
    assert result is not None

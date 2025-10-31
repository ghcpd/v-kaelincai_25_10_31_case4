"""Automated tests verifying deterministic and stable behavior."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import numpy as np
import pytest

from optimized_code import DeterministicScorer, ValidationError, build_default_scorer, process_file

ROOT = Path(__file__).parent
TEST_DATA = json.loads((ROOT / "test_data.json").read_text())


@pytest.fixture()
def scorer() -> DeterministicScorer:
    return build_default_scorer(seed=2025)


def test_baseline_deterministic(scorer: DeterministicScorer):
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "baseline_deterministic")
    payload = case["input"]
    results = [scorer.score(payload["transactions"]) for _ in range(10)]
    totals = {result["total_score"] for result in results}
    assert totals == {292.0}


def test_concurrency_is_stable(scorer: DeterministicScorer):
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "concurrency_race")
    payload = case["input"]

    outputs = []

    def worker():
        outputs.append(scorer.score(payload["transactions"]))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    totals = {tuple(o["trending_ids"]) for o in outputs}
    assert totals == {("C-100", "C-101")}


def test_state_independence(scorer: DeterministicScorer):
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "state_leakage")
    payload = case["input"]

    first = scorer.score(payload["transactions"])
    second = scorer.score(payload["transactions"])
    assert first == second


def test_malformed_payload_raises():
    case = next(c for c in TEST_DATA["cases"] if c["name"] == "malformed_payload")
    payload = case["input"]

    with pytest.raises(ValidationError):
        build_default_scorer().score(payload["transactions"])


def test_process_file_deterministic(tmp_path):
    data = {"transactions": []}
    file_path = tmp_path / "payload.json"
    file_path.write_text(json.dumps(data))

    runs = [process_file(file_path) for _ in range(5)]
    totals = [result["total_score"] for result in runs]
    assert np.std(totals) == 0.0

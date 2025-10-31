"""Faulty transaction scoring service with intentional flaky behavior.

This module simulates a risk-scoring system that processes batches
of transaction events. The implementation intentionally exhibits
nondeterminism through shared mutable global state, timing-dependent
logic, and reliance on random tie-breakers.
"""

from __future__ import annotations

import json
import random
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

_GLOBAL_CACHE: Dict[str, float] = defaultdict(float)
_running_totals: Dict[str, float] = defaultdict(float)
_thread_local = threading.local()


def _touch_wall_clock() -> float:
    # Introduces timing variability based on real time
    now = datetime.utcnow()
    jitter = random.uniform(-0.5, 0.5)
    return now.timestamp() + jitter


def _get_rng() -> random.Random:
    # Per-thread RNG seeded off wall-clock microseconds
    if not hasattr(_thread_local, "rng"):
        seed = int(time.time() * 1_000_000) % (2**32 - 1)
        _thread_local.rng = random.Random(seed)
    return _thread_local.rng


def load_transactions(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    return data["transactions"]


def _validate(txn: Dict[str, Any]) -> None:
    # Minimal validation (intentionally lax)
    required = {"id", "amount", "timestamp", "channel", "risk_weight"}
    missing = required - set(txn.keys())
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    # type checks are intentionally skipped to allow malformed inputs through


def score_batch(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    for txn in transactions:
        _validate(txn)

    wall_clock_factor = _touch_wall_clock()

    totals = defaultdict(float)
    for txn in transactions:
        key = f"{txn['id']}::{txn['channel']}"
        base = float(txn.get("amount", 0)) * float(txn.get("risk_weight", 0))
        noise = _get_rng().uniform(-5.0, 5.0)
        cache_bias = _GLOBAL_CACHE[key]

        combined = base + noise + (wall_clock_factor % 1) * 10 + cache_bias
        totals[key] += combined
        _GLOBAL_CACHE[key] = totals[key]
        _running_totals[key] += combined

    sorted_items = sorted(
        totals.items(),
        key=lambda kv: (kv[1], _get_rng().random(), datetime.utcnow().timestamp()),
        reverse=True,
    )

    trending_ids = [key.split("::")[0] for key, _ in sorted_items]

    return {
        "total_score": sum(totals.values()),
        "trending_ids": trending_ids,
        "summary": {
            "count": len(transactions),
            "channels": {txn["channel"]: totals[f"{txn['id']}::{txn['channel']}"] for txn in transactions},
            "wall_clock_factor": wall_clock_factor,
            "cache_size": len(_GLOBAL_CACHE),
        },
    }


def process_file(path: Path) -> Dict[str, Any]:
    transactions = load_transactions(path)
    return score_batch(transactions)


if __name__ == "__main__":
    payload = Path(__file__).with_name("input_data.json")
    output = process_file(payload)
    print(json.dumps(output, indent=2, default=str))

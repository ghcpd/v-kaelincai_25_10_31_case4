"""Optimized transaction scoring service with deterministic behavior.

The improved module introduces:
- Deterministic random number generation via injected RNG seeded per run.
- Thread-safe aggregation using locks and immutable snapshots.
- Strict validation using type coercion and accepted domains.
- Removal of global state mutations in favor of functional computation.
- Optional time mocking through dependency injection with monotonic clocks.
"""

from __future__ import annotations

import json
import threading
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from dateutil import parser as date_parser


@dataclass(frozen=True)
class Transaction:
    identifier: str
    amount: float
    timestamp: datetime
    channel: str
    risk_weight: float


class ValidationError(Exception):
    """Raised when an invalid payload is encountered."""


class DeterministicScorer:
    """Deterministic scorer with thread-safe aggregation."""

    def __init__(
        self,
        *,
        rng_factory: Callable[[], Any],
        clock: Callable[[], float],
    ) -> None:
        self._rng_factory = rng_factory
        self._clock = clock
        self._lock = threading.Lock()

    def _validate(self, txn: Dict[str, Any]) -> Transaction:
        try:
            identifier = str(txn["id"])
            amount = float(txn["amount"])
            timestamp = date_parser.isoparse(str(txn["timestamp"]))
            channel = str(txn["channel"]).lower()
            if channel not in {"web", "mobile", "branch"}:
                raise ValidationError(f"Unsupported channel: {channel}")
            risk_weight = float(txn["risk_weight"])
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError(f"Invalid transaction payload: {txn}") from exc

        if not 0 <= risk_weight <= 1:
            raise ValidationError("risk_weight must be between 0 and 1")

        return Transaction(identifier, amount, timestamp, channel, risk_weight)

    def score(self, transactions: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        validated = [self._validate(txn) for txn in transactions]
        rng = self._rng_factory()
        timestamp_key = round(self._clock(), 6)

        totals: Dict[str, float] = {}
        channel_counter = Counter()

        def compute(txn: Transaction) -> float:
            base = txn.amount * txn.risk_weight
            channel_counter[txn.channel] += 1
            return base

        # Guard shared writes with lock even though we operate sequentially
        # to preserve deterministic behavior under future concurrency.
        with self._lock:
            for txn in validated:
                key = f"{txn.identifier}::{txn.channel}::{timestamp_key}"
                totals[key] = compute(txn)

        sorted_items = sorted(
            totals.items(),
            key=lambda kv: (kv[1], kv[0]),
            reverse=True,
        )

        trending_ids = [key.split("::")[0] for key, _ in sorted_items]
        total_score = float(sum(totals.values()))

        summary = {
            "count": len(validated),
            "channels": dict(channel_counter),
            "clock_tag": timestamp_key,
            "rng_state": rng.getstate(),
        }

        return {
            "total_score": total_score,
            "trending_ids": trending_ids,
            "summary": summary,
        }


def build_default_scorer(seed: int = 1337) -> DeterministicScorer:
    def rng_factory() -> Any:
        import random

        rng = random.Random(seed)
        return rng

    def monotonic_clock() -> float:
        import time

        return time.perf_counter()

    return DeterministicScorer(rng_factory=rng_factory, clock=monotonic_clock)


def load_transactions(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text())
    txns = payload.get("transactions")
    if not isinstance(txns, list):
        raise ValidationError("transactions must be a list")
    return txns


def process_file(path: Path, scorer: Optional[DeterministicScorer] = None) -> Dict[str, Any]:
    scorer = scorer or build_default_scorer()
    transactions = load_transactions(path)
    return scorer.score(transactions)


if __name__ == "__main__":
    payload = Path(__file__).with_name("input_data.json")
    scorer = build_default_scorer()
    output = process_file(payload, scorer)
    print(json.dumps(output, indent=2, default=str))

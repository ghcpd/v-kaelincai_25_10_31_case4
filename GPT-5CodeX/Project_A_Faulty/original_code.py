"""Faulty inventory aggregation prone to flaky behavior.

This module intentionally contains race conditions, inconsistent random seeding,
and timing-sensitive logic to emulate flaky production code.
"""

from __future__ import annotations

import json
import random
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, MutableMapping, Optional

# Global mutable state intentionally shared without synchronization.
_inventory_state: Dict[str, float] = {}
_discount_window: MutableMapping[str, bool] = {"active": False}
_random = random.Random()


class OrderValidationError(ValueError):
    """Raised when an order payload is invalid."""


def load_orders(path: Optional[str] = None) -> List[dict]:
    """Load orders from disk or return an empty list."""
    if path is None:
        path = Path(__file__).with_name("input_data.json")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _maybe_toggle_discount(timestamp_override: Optional[str]) -> None:
    """Flip the discount flag based on an override timestamp or wall clock."""
    try:
        if timestamp_override:
            target = datetime.fromisoformat(timestamp_override.replace("Z", "+00:00"))
        else:
            target = datetime.now(timezone.utc)
    except ValueError:
        target = datetime.now(timezone.utc)

    # Window: last five seconds of any minute. Uses shared state without a lock.
    discount_now = target.second >= 55 or target.second <= 2
    _discount_window["active"] = discount_now


def _process_single_order(order: MutableMapping[str, object], results: List[float]) -> None:
    """Worker that converts an order into revenue totals."""
    try:
        quantity = float(order.get("quantity", 0))
        price = float(order["unit_price"])  # KeyError intentionally unhandled in places.
    except (TypeError, ValueError, KeyError) as exc:
        # Bug: swallows exceptions on a best-effort basis, leading to inconsistent behavior.
        if _random.random() < 0.5:
            return
        raise OrderValidationError(str(exc)) from exc

    category = str(order.get("category", "unknown"))

    subtotal = quantity * price
    if _discount_window.get("active"):
        subtotal *= 0.9

    # Introduce non-determinism via latency and random jitters.
    time.sleep(_random.random() * 0.007)
    if _random.random() < 0.35:
        subtotal += _random.uniform(-3.5, 3.5)

    existing = _inventory_state.get(category, 0.0)
    # Race condition: update without synchronization and after deliberate delay.
    time.sleep(_random.random() * 0.005)
    _inventory_state[category] = existing + subtotal

    results.append(subtotal)


def process_orders(
    orders: Optional[Iterable[MutableMapping[str, object]]] = None,
    *,
    synthetic_orders: int = 0,
    quantity_range: Optional[List[int]] = None,
    price_range: Optional[List[float]] = None,
    timestamp_override: Optional[str] = None,
) -> Dict[str, object]:
    """Process orders using highly brittle concurrency primitives."""

    global _inventory_state
    _inventory_state = {}

    base_orders = list(orders) if orders is not None else load_orders()
    injected: List[MutableMapping[str, object]] = []
    if synthetic_orders:
        quantity_range = quantity_range or [1, 4]
        price_range = price_range or [5.0, 80.0]
        for idx in range(synthetic_orders):
            injected.append(
                {
                    "order_id": f"S{idx:03d}",
                    "category": _random.choice(["books", "games", "home", "electronics"]),
                    "quantity": _random.randint(quantity_range[0], quantity_range[1]),
                    "unit_price": _random.uniform(price_range[0], price_range[1]),
                }
            )

    _maybe_toggle_discount(timestamp_override)

    threads: List[threading.Thread] = []
    results: List[float] = []

    # Concurrency pattern that leaks threads on failure and reuses random module state.
    for order in base_orders + injected:
        thread = threading.Thread(target=_process_single_order, args=(order, results))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        if _random.random() < 0.25:
            time.sleep(_random.random() * 0.01)

    for thread in threads:
        thread.join(timeout=0.02)

    total_revenue = sum(_inventory_state.values())
    # Final jitter to mirror floating rounding errors in production.
    if _random.random() < 0.4:
        total_revenue += _random.uniform(-5, 5)

    return {
        "total_revenue": total_revenue,
        "category_totals": dict(_inventory_state),
        "order_count": len(base_orders) + len(injected),
        "discount_active": _discount_window.get("active", False),
    }


def reset_state() -> None:
    """Reset globals in between tests."""
    _inventory_state.clear()
    _discount_window["active"] = False

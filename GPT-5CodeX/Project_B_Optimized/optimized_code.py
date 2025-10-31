"""Optimised, deterministic inventory aggregation implementation."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, Iterable, List, MutableMapping, Optional, Sequence, Tuple

CATEGORY_SEQUENCE: Tuple[str, ...] = ("books", "games", "electronics", "home")
QUANTIZER = Decimal("0.01")


class OrderValidationError(ValueError):
    """Raised when an order payload is invalid."""


@dataclass(frozen=True)
class ProcessConfig:
    synthetic_orders: int = 0
    quantity_range: Sequence[int] = (1, 1)
    price_range: Sequence[float] = (0.0, 0.0)
    timestamp_override: Optional[str] = None


def load_orders(path: Optional[str] = None) -> List[dict]:
    path = Path(path) if path else Path(__file__).with_name("input_data.json")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(QUANTIZER, rounding=ROUND_HALF_UP)


def _determine_discount(timestamp_override: Optional[str]) -> bool:
    if not timestamp_override:
        now = datetime.now(timezone.utc)
    else:
        try:
            now = datetime.fromisoformat(timestamp_override.replace("Z", "+00:00"))
        except ValueError as exc:
            raise OrderValidationError(f"Invalid timestamp_override: {timestamp_override}") from exc
    return now.second >= 55 or now.second <= 2


def _validate_order(order: MutableMapping[str, object]) -> MutableMapping[str, object]:
    missing = {field for field in ("category", "quantity", "unit_price") if field not in order}
    if missing:
        raise OrderValidationError(f"Missing required fields: {sorted(missing)}")

    try:
        float(order["unit_price"])
        float(order["quantity"])
    except (TypeError, ValueError) as exc:
        raise OrderValidationError("Quantity and unit_price must be numeric") from exc

    category = str(order["category"])
    if not category:
        raise OrderValidationError("Category must be a non-empty string")
    return order


def _build_synthetic_orders(config: ProcessConfig) -> List[dict]:
    count = int(config.synthetic_orders or 0)
    if count <= 0:
        return []

    q_start, q_end = map(int, config.quantity_range)
    if q_start <= 0 or q_end < q_start:
        raise OrderValidationError("quantity_range must be positive and non-decreasing")

    p_start, p_end = map(Decimal, config.price_range)
    if p_start < Decimal("0") or p_end < p_start:
        raise OrderValidationError("price_range must be non-negative and non-decreasing")

    q_span = q_end - q_start + 1
    p_span = p_end - p_start

    synthetic: List[dict] = []
    divisor = count - 1 if count > 1 else 1

    for idx in range(count):
        category = CATEGORY_SEQUENCE[idx % len(CATEGORY_SEQUENCE)]
        quantity = q_start + (idx % q_span)
        fraction = Decimal(idx) / Decimal(divisor)
        price = p_start + (p_span * fraction)
        synthetic.append(
            {
                "order_id": f"S{idx:03d}",
                "category": category,
                "quantity": quantity,
                "unit_price": float(_quantize(price)),
            }
        )
    return synthetic


def _normalise_orders(orders: Iterable[MutableMapping[str, object]]) -> List[dict]:
    normalised: List[dict] = []
    for order in orders:
        validated = _validate_order(order)
        normalised.append(
            {
                "order_id": str(validated.get("order_id", "")),
                "category": str(validated["category"]),
                "quantity": float(validated["quantity"]),
                "unit_price": float(validated["unit_price"]),
            }
        )
    return normalised


def _worker(order: MutableMapping[str, object], discount_multiplier: Decimal) -> Tuple[str, Decimal]:
    quantity = Decimal(str(order["quantity"]))
    price = Decimal(str(order["unit_price"]))
    subtotal = _quantize(quantity * price * discount_multiplier)
    return order["category"], subtotal


def process_orders(
    orders: Optional[Iterable[MutableMapping[str, object]]] = None,
    *,
    synthetic_orders: int = 0,
    quantity_range: Sequence[int] = (1, 1),
    price_range: Sequence[float] = (0.0, 0.0),
    timestamp_override: Optional[str] = None,
) -> Dict[str, object]:
    """Process orders deterministically and aggregate revenue per category."""

    base_orders = list(orders) if orders is not None else load_orders()
    config = ProcessConfig(
        synthetic_orders=synthetic_orders,
        quantity_range=quantity_range,
        price_range=price_range,
        timestamp_override=timestamp_override,
    )

    work_orders = _normalise_orders(base_orders) + _build_synthetic_orders(config)
    discount_active = _determine_discount(timestamp_override)
    discount_multiplier = Decimal("0.90") if discount_active else Decimal("1.00")

    category_totals: Dict[str, Decimal] = {}
    total_revenue = Decimal("0")

    # Executor preserves input order; aggregation happens on the main thread to remain deterministic.
    max_workers = min(8, max(len(work_orders), 1))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for category, subtotal in executor.map(
            lambda order: _worker(order, discount_multiplier), work_orders
        ):
            category_totals[category] = category_totals.get(category, Decimal("0")) + subtotal
            total_revenue += subtotal

    serialised_totals = {category: float(_quantize(total)) for category, total in category_totals.items()}

    return {
        "total_revenue": float(_quantize(total_revenue)),
        "category_totals": serialised_totals,
        "order_count": len(work_orders),
        "discount_active": discount_active,
    }


def reset_state() -> None:
    """Provided for API parity; no global state to reset."""
    return None

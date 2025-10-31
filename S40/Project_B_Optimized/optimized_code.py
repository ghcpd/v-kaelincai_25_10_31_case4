import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Iterable, List, Tuple

_RANDOM = random.Random(42)  # Deterministic seed

@dataclass(frozen=True)
class Order:
    id: str
    amount: float
    region: str
    priority: int
    items: int

class RateProvider:
    def __init__(self) -> None:
        self._cache: Dict[str, float] = {}
        self._lock = Lock()

    def get_rate(self, region: str) -> float:
        with self._lock:
            if region not in self._cache:
                base = 10.0 + (_RANDOM.random() - 0.5) * 2
                self._cache[region] = max(1.0, round(base, 2))
            return self._cache[region]

class DiscountEngine:
    def __init__(self, deterministic_clock: Tuple[int, ...] | None = None) -> None:
        self._clock_iter = iter(deterministic_clock or (14,))
        self._lock = Lock()

    def apply(self, amount: float, priority: int) -> float:
        with self._lock:
            try:
                hour = next(self._clock_iter)
            except StopIteration:
                hour = 14
        if hour % 2 == 0:
            return amount * (1 - min(priority * 0.02, 0.15))
        return amount

class OrderProcessor:
    def __init__(self, rate_provider: RateProvider, discount_engine: DiscountEngine, workers: int = 4) -> None:
        self._rate_provider = rate_provider
        self._discount_engine = discount_engine
        self._workers = workers

    def _process_one(self, order: Order) -> Dict[str, Any]:
        rate = self._rate_provider.get_rate(order.region)
        discounted = self._discount_engine.apply(order.amount, order.priority)
        shipping_cost = round(rate * max(1, order.items), 2)
        return {
            "id": order.id,
            "shipping_cost": shipping_cost,
            "discounted_amount": round(discounted, 2),
            "region": order.region,
            "timestamp": 0.0,
        }

    def process(self, orders: Iterable[Order]) -> List[Dict[str, Any]]:
        orders_list = list(orders)
        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self._workers) as executor:
            future_map = {executor.submit(self._process_one, order): order.id for order in orders_list}
            for future in as_completed(future_map):
                results.append(future.result())
        results.sort(key=lambda entry: entry["id"])
        return results

def _normalize(order_data: Dict[str, Any]) -> Order:
    return Order(
        id=str(order_data["id"]),
        amount=float(order_data.get("amount", 0.0)),
        region=str(order_data.get("region", "UNKNOWN")),
        priority=int(order_data.get("priority", 0)),
        items=int(order_data.get("items", 1)),
    )

def process_orders(path: Path, workers: int = 4) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    orders = [_normalize(entry) for entry in data]
    processor = OrderProcessor(RateProvider(), DiscountEngine((10,) * len(orders)), workers=workers)
    return processor.process(orders)

if __name__ == "__main__":
    data_path = Path(__file__).with_name("input_data.json")
    output = process_orders(data_path)
    print(json.dumps(output, indent=2))

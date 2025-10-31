import json
import random
import time
import threading
from pathlib import Path
from typing import Any, Dict, List

# Global mutable state shared across threads, causing races
_SHIPPING_CACHE: Dict[str, float] = {}
_LOCKED_REGIONS: List[str] = []  # List is mutated without synchronization

def _load_orders(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def _simulate_external_latency() -> None:
    # Random sleep introduces timing nondeterminism
    time.sleep(random.uniform(0.01, 0.2))

def _fetch_dynamic_rate(region: str) -> float:
    # Flaky: rate depends on random fluctuation and shared cache
    if region in _SHIPPING_CACHE and random.random() > 0.3:
        return _SHIPPING_CACHE[region]
    base_rate = random.uniform(5.0, 15.0)
    fluctuation = random.gauss(0, 1.5)
    rate = max(1.0, base_rate + fluctuation)
    # Race condition: multiple threads write without locking
    _SHIPPING_CACHE[region] = rate
    return rate

def _apply_discount(amount: float, priority: int) -> float:
    # Time-based discount (flaky due to wall clock)
    local_hour = time.localtime().tm_hour
    if local_hour % 2 == 0:
        return amount * (1 - min(priority * 0.03, 0.2))
    return amount

def calculate_shipping_cost(order: Dict[str, Any]) -> Dict[str, Any]:
    region = order.get("region")
    if region is None:
        raise ValueError("order missing region")

    if region in _LOCKED_REGIONS:
        # Unreliable guard causing inconsistent access
        raise RuntimeError(f"Region {region} temporarily locked")

    # Randomly lock regions to simulate flakiness
    if random.random() < 0.15:
        _LOCKED_REGIONS.append(region)

    _simulate_external_latency()
    rate = _fetch_dynamic_rate(region)
    total = _apply_discount(order.get("amount", 0.0), order.get("priority", 0))

    # Random fault injection for concurrency stress
    if random.random() < 0.1:
        raise RuntimeError("Simulated downstream failure")

    return {
        "id": order.get("id"),
        "shipping_cost": round(rate * max(1, order.get("items", 1)), 2),
        "discounted_amount": round(total, 2),
        "region": region,
        "timestamp": time.time(),
    }

def process_orders(path: Path, workers: int = 4) -> List[Dict[str, Any]]:
    orders = _load_orders(path)
    results: List[Dict[str, Any]] = []
    errors: List[Exception] = []

    def worker(chunk: List[Dict[str, Any]]):
        for order in chunk:
            try:
                result = calculate_shipping_cost(order)
                results.append(result)
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

    # Chunk orders per worker without consistent sizing
    chunks = [orders[i::workers] for i in range(workers)]
    threads = [threading.Thread(target=worker, args=(chunk,), daemon=True) for chunk in chunks]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    if errors:
        raise RuntimeError(f"Processing failed with {len(errors)} errors: {errors}")

    return results

if __name__ == "__main__":
    data_path = Path(__file__).with_name("input_data.json")
    output = process_orders(data_path)
    print(json.dumps(output, indent=2))

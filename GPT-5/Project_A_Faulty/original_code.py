"""Original faulty implementation exhibiting flaky behavior.
Scenario: Concurrent summation of numeric inputs using threads with time-dependent skips,
random failures, and unsafely shared mutable global state causing nondeterministic results.
"""
from __future__ import annotations
import threading
import time
import random
from typing import Any, Dict, List

# Global mutable state (flaky): counts drops and holds last timestamps
GLOBAL_DROP_COUNT = 0
GLOBAL_TIMESTAMPS: List[int] = []
GLOBAL_LOCKLESS_RESULTS: List[int] = []  # appended without locks

# Intentionally NOT seeding randomness -> nondeterministic across runs

def _worker(value: Any, results: List[int]):
    global GLOBAL_DROP_COUNT
    try:
        # Simulate variable timing
        sleep_dur = random.random() / 100.0  # 0 - 0.01s
        time.sleep(sleep_dur)
        now_ms = int(time.time() * 1000)
        GLOBAL_TIMESTAMPS.append(now_ms)
        # Time-based flaky drop: if current ms modulo 7 == 0 skip value
        if now_ms % 7 == 0:
            GLOBAL_DROP_COUNT += 1
            return
        # Random failure raising exception (10%) leading to silent loss
        if random.random() < 0.10:
            raise RuntimeError("Simulated transient failure")
        if isinstance(value, (int, float)):
            # Another flaky branch: sometimes double-add (current ms modulo 11)
            if now_ms % 11 == 0:
                results.append(value)
            results.append(value)
        else:
            # Non-numeric ignored silently (flaky handling)
            GLOBAL_DROP_COUNT += 1
    except Exception:
        # Swallow exception -> lost contribution
        GLOBAL_DROP_COUNT += 1
        return


def process_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single test case returning potentially inconsistent result.
    Input format: {"id": str, "inputs": List[Any], ...}
    Returns dict with result (sum) and diagnostics.
    """
    inputs = case.get("inputs", [])
    threads: List[threading.Thread] = []
    local_results: List[int] = GLOBAL_LOCKLESS_RESULTS  # use shared list intentionally
    start = time.perf_counter()
    for v in inputs:
        t = threading.Thread(target=_worker, args=(v, local_results))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    end = time.perf_counter()
    # Flaky sum: because shared list contains previous runs too and possible duplicates
    total = sum(local_results)
    return {
        "case_id": case.get("id"),
        "reported_sum": total,
        "drop_count": GLOBAL_DROP_COUNT,
        "global_ts_count": len(GLOBAL_TIMESTAMPS),
        "duration_sec": end - start,
        "inputs_count": len(inputs)
    }


def main():
    # Simple manual run example
    demo_case = {"id": "demo", "inputs": [1,2,3,4,5]}
    for i in range(3):
        print(f"Run {i}", process_case(demo_case))

if __name__ == "__main__":
    main()

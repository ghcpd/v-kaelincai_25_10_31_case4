# Flaky Behavior Scenario

## Title
Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Flaky Behavior Detection, Mitigation, and Optimization

## Overview
This experiment models a transaction scoring service exposed through a Python module. The service ingests a batch of transaction events, then computes prioritized recommendations for fraud analysts. The legacy implementation in **Project A (Faulty)** relies on shared global caches, nondeterministic tie-breaking logic, and wall-clock timing, which together introduce flakiness when identical payloads are processed repeatedly or concurrently.

## Input Format
- Type: JSON (list of Python dictionaries when loaded)
- Schema per transaction:
  ```json
  {
    "id": "<string>",
    "amount": <number>,
    "timestamp": "<ISO 8601 string>",
    "channel": "web" | "mobile" | "branch",
    "risk_weight": <number between 0 and 1>
  }
  ```
- Batch payload stored under the key `"transactions"` inside `input_data.json` for each project.

## Output Format
- Dictionary/JSON with:
  - `"total_score"`: aggregated float score across transactions.
  - `"trending_ids"`: ordered list of transaction IDs.
  - `"summary"`: nested metrics including count, mean, and channel histograms.

## Flaky Behavior Type (Project A)
- **Race Conditions:** Shared mutable cache `_GLOBAL_CACHE` and `_running_totals` are updated from multiple threads without locking, occasionally dropping increments.
- **Nondeterministic Ordering:** Sorting uses `random.uniform` and `datetime.utcnow()` for tie-breaking, leading to inconsistent `trending_ids` across runs.
- **Time Sensitivity:** Wall-clock microsecond values leak into scoring, so results depend on system load and execution timing.
- **State Leakage:** Global structures retain values across runs, causing later invocations to incorporate stale data.

## Intended Mitigation Outcomes (Project B)
- Deterministic scoring pipeline with explicit seeding (`random.Random(seed)`), stable sorting keys, and idempotent aggregation.
- Thread-safe updates through `threading.Lock` and immutable data snapshots to prevent state leakage.
- Controlled timing by mocking a monotonic clock and dependency injection for any temporal references.
- Comprehensive validation and defensive copying to block malformed inputs from corrupting shared state.

## Success Criteria
1. Repeated runs (N ≥ 20) over identical input batches return identical outputs in Project B, while Project A exhibits at least one deviation.
2. Stability rate improves from < 70% in Project A to ≥ 99% in Project B.
3. Average runtime variance (stddev) for trending computation decreases by at least 50% post-optimization.
4. Edge cases (empty payloads, malformed records, extreme values) are handled deterministically with descriptive errors.

## Test Data Strategy
Five structured scenarios captured in each project's `test_data.json` cover:
1. **Baseline Deterministic Batch** – expected consistent scores.
2. **Concurrency Stress Batch** – duplicates forcing tie-breaking and shared cache contention.
3. **Boundary Empty Batch** – ensures deterministic zero output.
4. **Malformed Input** – verifies validation paths.
5. **State Leakage Probe** – re-uses payloads across runs to ensure independence.

These scenarios drive both `pytest` suites and the automated harness scripts that sample outputs across repeated executions.

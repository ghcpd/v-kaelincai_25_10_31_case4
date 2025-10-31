# Comparison Report

## Overview
This report compares Project A (faulty) and Project B (optimized) implementations for detecting and mitigating flaky behavior in a transaction scoring service. Metrics are derived from the automated harness (`run_all.sh`) which runs each project for `N` iterations (default `20`).

## Stability Metrics
| Metric | Project A | Project B | Improvement |
|--------|-----------|-----------|-------------|
| Stability rate (% consistent runs) | TBD | TBD | TBD |
| Average runtime (s) | TBD | TBD | TBD |
| Runtime stddev (s) | TBD | TBD | TBD |
| Failure count | TBD | TBD | TBD |

> Run `./run_all.sh` after executing setup scripts to populate actual values.

## Per-Test Observations
| Test Case | Flaky Behavior Type | Project A Result | Project B Result | Notes |
|-----------|---------------------|------------------|------------------|-------|
| baseline_deterministic | control | Inconsistent totals due to random noise | Deterministic totals and ordering | RNG seeding removed variability |
| concurrency_race | race_condition | Trending order differs per run | Stable ordering with lock protection | Locking and per-run RNG seeds |
| empty_batch | boundary | Occasionally inherits stale cache values | Deterministic zero output | Global state removed |
| malformed_payload | validation | May throw various exceptions | Predictable `ValidationError` | Strict validation with typed coercion |
| state_leakage | stateful | Totals drift after repeated runs | Totals remain constant | Immutable scorer state |

## Mitigation Strategies
- Deterministic RNG seeded per invocation.
- Thread-safe aggregation with `threading.Lock` and immutable results.
- Strict validation pipeline with explicit error types.
- Removal of global caches; results built from scratch each run.
- Clock injection providing stable `clock_tag` metric.

## Residual Risks & Recommendations
- External integration points (not simulated here) should adopt similar locking and deterministic seeding strategies.
- Consider running tests under varying CPU loads with `pytest -n auto` to stress concurrency.
- For production, wrap scoring service in circuit-breakers and idempotency keys when interacting with external systems.

## Reproducibility Notes
- Ensure `setup_original.sh` and `setup_optimized.sh` are executed prior to running tests.
- Logs (`log_original.txt`, `log_optimized.txt`) and timing reports (`time_original.txt`, `time_optimized.txt`) populate after harness execution.
- The aggregated metrics above update once `run_all.sh` completes and writes structured data.

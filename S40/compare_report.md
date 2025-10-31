# Comparison Report: Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Flaky Behavior Detection, Mitigation, and Optimization

## Scenario Summary
- **Domain**: Concurrent shipping cost calculation with shared mutable cache
- **Flaky Behavior**: Randomized latency, unsynchronized caches, and time-based discounts cause nondeterministic outputs, intermittent exceptions, and race conditions.
- **Mitigation**: Deterministic seeding, thread-safe caching, immutable data structures, deterministic clock injection, and controlled thread execution order.

## Metrics Overview
| Metric | Project A (Faulty) | Project B (Optimized) |
| --- | --- | --- |
| Stability Rate (consistent runs %) | TODO | TODO |
| Avg Runtime (s) | TODO | TODO |
| Runtime StdDev | TODO | TODO |
| Failure Count | TODO | TODO |
| Edge Case Coverage | TODO | TODO |

> **Note**: Replace `TODO` values after executing `run_all.sh` which aggregates actual results.

## Test Case Comparison
| Test Case | Flaky Type | Project A Outcome | Project B Outcome |
| --- | --- | --- | --- |
| baseline_order_processing | Nondeterministic outputs | Expected variability | Deterministic | 
| concurrent_race_condition | Race condition | Intermittent `RuntimeError` | Stable | 
| boundary_missing_region | Validation | `ValueError` consistently | `KeyError` consistently |
| invalid_payload_structure | Malformed input | Deterministic `TypeError` | Deterministic `TypeError` |
| hidden_state_lock_leak / reseeded_determinism_check | Shared mutable state | Lock leak persists | Rate consistent |

## Mitigation Strategies Applied
1. **Deterministic Random Source**: Shared `_RANDOM` instance with fixed seed prevents divergence in rate calculations.
2. **Thread-Safe Cache**: `RateProvider` uses `Lock` to guard cache updates, eliminating races.
3. **Idempotent Discount Engine**: Deterministic clock sequence ensures repeatable discounts regardless of system time.
4. **Immutable Order Representation**: `@dataclass(frozen=True)` ensures orders are read-only, preventing hidden state mutation.
5. **Ordered Aggregation**: Sorting results maintains consistent output ordering across runs.

## Residual Risks & Recommendations
- **Residual Nondeterminism**: External dependencies not mocked may reintroduce variability; maintain mocks/stubs for new integrations.
- **Performance Scaling**: Larger datasets may require batching strategies and instrumentation to ensure locks do not become contention points.
- **Further Enhancements**: Consider structured logging, metrics dashboard integration, and chaos simulations to validate robustness under high load.

## Execution Instructions
1. Run `bash Project_A_Faulty/setup_original.sh` and `bash Project_B_Optimized/setup_optimized.sh` if environments are not initialized.
2. Execute `bash run_all.sh` at repository root to generate metrics and populate this report.
3. Review `log_*.txt`, `time_*.txt`, and `results_*.json` files within each project for detailed run data.

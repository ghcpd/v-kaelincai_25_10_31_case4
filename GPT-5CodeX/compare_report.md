# Comparison Report

## Aggregate Stability
- Project A (Faulty): 0 / 5 runs stable (0.0%)
- Project B (Optimized): 5 / 5 runs stable (100.0%)
- Average runtime delta: +0.0308 seconds per run

## Per-Test Metrics
| Case | A Stability | B Stability | A Avg (s) | B Avg (s) | A Failures | B Failures |
|---|---|---|---|---|---|---|
| case_01 | 40.0% | 100.0% | 0.0136 | 0.0085 | 3 | 0 |
| case_02 | 20.0% | 100.0% | 0.0212 | 0.0110 | 4 | 0 |
| case_03 | 100.0% | 100.0% | 0.0099 | 0.0076 | 0 | 0 |
| case_04 | 60.0% | 100.0% | 0.0044 | 0.0037 | 2 | 0 |
| case_05 | 80.0% | 100.0% | 0.0099 | 0.0083 | 1 | 0 |

## Mitigation Strategies
- Introduced deterministic synthetic order generation and Decimal rounding to remove floating jitter.
- Removed shared mutable state, performing aggregation on the main thread with executor coordination.
- Implemented strict validation and structured exceptions to ensure malformed inputs fail fast.
- Normalised time-based discount logic with explicit parsing and deterministic evaluation.
- Added high-volume repeated-run harness with structured metrics for reproducibility.

## Residual Risks & Next Steps
- Performance measurements are taken on the local machine and may still fluctuate due to system load.
- External integrations (e.g., real payment gateways) are mocked; additional contract tests are recommended.
- Long-running workloads may benefit from adaptive batch sizing or async IO to further reduce latency variance.

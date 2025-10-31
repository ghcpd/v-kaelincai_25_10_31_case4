# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Flaky Behavior Detection, Mitigation, and Optimization

## Overview
This repository provides two Python projects designed to illustrate flaky behavior detection and mitigation:

- **Project_A_Faulty**: Demonstrates nondeterministic shipping cost calculations caused by shared mutable state, timing dependencies, and random latency.
- **Project_B_Optimized**: Presents a hardened, deterministic solution leveraging deterministic seeding, thread-safe caching, immutable objects, and controlled timing injection.

## Flaky Scenario Description
- **Input Format**: JSON file containing orders with fields `id`, `amount`, `region`, `priority`, and `items`.
- **Output Format**: JSON list containing `id`, `shipping_cost`, `discounted_amount`, `region`, and `timestamp`.
- **Flaky Behavior (Project A)**: Random sleep latency, unsynchronized cache writes, wall-clock dependent discounts, and concurrency issues produce inconsistent outputs and intermittent exceptions.
- **Mitigation (Project B)**: Deterministic RNG seed, thread-safe rate provider, deterministic virtual clock, and result sorting ensure consistent outputs across repeated runs.

## Quick Start
1. Ensure Bash compatible environment (e.g., Git Bash on Windows, macOS/Linux shell).
2. Run the master script:
   ```bash
   bash run_all.sh
   ```
   This script:
   - Sets up virtual environments for both projects.
   - Executes flaky tests followed by optimized tests.
   - Aggregates results into `aggregate_results.json` and updates `compare_report.md`.

## Project Execution Details
### Project A (Faulty)
```bash
cd Project_A_Faulty
bash setup_original.sh
bash run_original.sh
```
- **Artifacts**: `log_original.txt`, `time_original.txt`, `results_original.json`.
- **Behaviour**: Expect intermittent failures and output variability.

### Project B (Optimized)
```bash
cd Project_B_Optimized
bash setup_optimized.sh
bash run_optimized.sh
```
- **Artifacts**: `log_optimized.txt`, `time_optimized.txt`, `results_optimized.json`.
- **Behaviour**: Outputs should remain stable across repeated runs.

## Test Data
- Root-level `test_data.json` summarizes the shared test cases and expected behaviors.
- Project-level `test_data.json` files tailor scenarios to each implementation.

## Reproducibility Strategies
- Deterministic seeding using `_RANDOM = random.Random(42)` for optimized version.
- Thread-safe caching with locks to prevent races.
- Deterministic clock injection in `DiscountEngine` to eliminate wall clock dependencies.
- Execution scripts instrumented with `/usr/bin/time` and pytest JSON reports for consistent logging.
- Optional Dockerization can be added by wrapping setup scripts in container runtime.

## Known Limitations & Future Work
- `/usr/bin/time` may require GNU `time`; adapt for non-Linux environments.
- Additional mocks may be required to isolate external services in extended scenarios.
- Stress testing under extreme loads is not covered; consider chaos engineering tools for broader validation.

## Files and Deliverables
- `Project_A_Faulty/`: Faulty implementation sources, tests, scripts, and logs.
- `Project_B_Optimized/`: Optimized implementation sources, tests, scripts, and logs.
- `compare_report.md`: Summary of stability improvements.
- `aggregate_results.json`: Aggregated logs and metrics after running `run_all.sh`.
- `run_all.sh`: Master execution script.
- `README.md`: This document.

## Next Steps
- Extend benchmarking coverage with load testing scenarios.
- Integrate CI pipeline with repeated run harness.
- Add Dockerfiles to guarantee environment parity across machines.

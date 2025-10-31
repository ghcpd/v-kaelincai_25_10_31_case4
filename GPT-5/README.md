# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Flaky Behavior Detection, Mitigation, and Optimization

## Overview
This repository contains two Python projects demonstrating detection and mitigation of flaky behavior:
- `Project_A_Faulty`: Original implementation with intentional nondeterminism (time-based skips, random failures, shared mutable state without isolation).
- `Project_B_Optimized`: Hardened version providing deterministic results via seeding, retries, validation, and thread-safe accumulation.

The shared `test_data.json` defines five cases covering normal, race-condition susceptibility, boundary, invalid input, and time-dependent flakiness.

## Flaky Scenario Description
The faulty implementation concurrently sums numeric values while:
- Random sleeps and unseeded randomness cause nondeterministic timing.
- Millisecond-based modulo condition causes intermittent value drops.
- Exceptions are swallowed, silently losing contributions.
- Shared global result list accumulates from previous runs.

Mitigation in the optimized version includes deterministic seeding, removing time-based skipping, retry/backoff logic, input validation, and isolation of per-run state.

## Files & Structure
- `Project_A_Faulty/original_code.py`: Flaky implementation.
- `Project_A_Faulty/test_original.py`: Repeated-run harness exposing instability.
- `Project_B_Optimized/optimized_code.py`: Stabilized implementation.
- `Project_B_Optimized/test_optimized.py`: Repeated-run harness verifying determinism.
- `test_data.json`: Shared test case definitions.
- `run_all.sh`: Orchestrates both projects and generates `compare_report.md`.

## Setup & Execution
Prerequisite: Python 3.10+ and Bash (Git Bash or WSL on Windows).

### Run Faulty Project
```bash
cd Project_A_Faulty
bash run_original.sh
```
Artifacts: `results_original.json`, `log_original.txt`, `time_original.txt`.

### Run Optimized Project
```bash
cd ../Project_B_Optimized
bash run_optimized.sh
```
Artifacts: `results_optimized.json`, `log_optimized.txt`, `time_optimized.txt`.

### Full Evaluation
```bash
cd ..
bash run_all.sh
```
Generates `compare_report.md` summarizing stability and performance improvements.

## Reproducibility Strategies
- Deterministic seed: `random.seed(42)` in optimized version.
- Removed wall-clock dependent skip logic.
- Isolated per-run state; no global accumulation.
- Structured repeated-run testing (15 runs per case) quantifies stability.
- Retry logic ensures transient failures are handled deterministically.

## Docker (Optional)
A Dockerfile can be added to standardize environment and timing if needed.

## Known Limitations & Next Steps
- Timing variance across runs remains due to OS scheduling; results deterministic regardless.
- No network/external I/O mocking included; could extend to simulate unstable APIs.
- Could expand metrics: percentiles, memory usage.
- Add property-based tests for broader input coverage.

## Metrics Interpretation
Stability rate = fraction of runs matching expected or within variance threshold.
Unique results >1 in faulty version indicate nondeterminism.

## License
Provided for experimental evaluation of AI model capabilities in flaky behavior mitigation.

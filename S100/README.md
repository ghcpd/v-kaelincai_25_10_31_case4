# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Flaky Behavior Detection, Mitigation, and Optimization

## Overview
This repository contains two Python projects for assessing flaky behavior mitigation strategies in a transaction scoring service.

- **Project A – Pre-Optimization (`Project_A_Faulty`)** demonstrates a legacy, flaky implementation with race conditions, random tie-breaking, and global state leakage.
- **Project B – Post-Optimization (`Project_B_Optimized`)** delivers a hardened, deterministic scorer featuring thread-safety, strict validation, deterministic seeding, and reproducible clocks.

The experiment surfaces how AI-assisted iterations can remediate flaky logic while improving both correctness and performance.

## Repository Structure
```
Project_A_Faulty/
Project_B_Optimized/
SCENARIO.md
compare_report.md
run_all.sh
test_data.json
README.md
```

Each project folder contains:
- Implementation module (`original_code.py` / `optimized_code.py`)
- Test harness (`test_original.py` / `test_optimized.py`)
- Execution scripts (`run_original.sh` / `run_optimized.sh`)
- Environment requirements (`requirements_*.txt`, `setup_*.sh`)
- Placeholder logs and timing reports populated upon running the harness (`log_*.txt`, `time_*.txt`, `results_*.json`)
- Shared test scenarios (`test_data.json`) tailored to highlight flaky patterns.

## Flaky Behavior Scenario
Detailed description is available in `SCENARIO.md`. Key points:
- Input: JSON payload containing a list of transactions.
- Output: Aggregate risk metrics including ordered trending IDs.
- Project A exhibits nondeterministic outputs due to random tie-breakers, global cache leakage, and wall-clock jitter.
- Project B mitigates flakiness with deterministic RNG, locks, validation, and dependency injection for clocks.

## Setup Instructions
### Common Steps
1. Ensure Python 3.11+ is available.
2. From the repository root, execute `bash run_all.sh` (WSL or Git Bash on Windows) or run the individual project scripts as outlined below.
3. For Windows PowerShell users, invoke `wsl bash run_all.sh` or adapt the commands using the created virtual environments (`.venv_original`, `.venv_optimized`).

### Project A (Faulty)
```bash
cd Project_A_Faulty
bash setup_original.sh
bash run_original.sh 20
```
This command runs 20 repeated test cycles, generating:
- `log_original.txt`: cumulative test output with intermittent failures.
- `time_original.txt`: per-run latencies.
- `results_original.json`: structured summary for comparison.

### Project B (Optimized)
```bash
cd Project_B_Optimized
bash setup_optimized.sh
bash run_optimized.sh 20
```
Outputs mirror Project A but demonstrate improved stability and reduced variance.

### Combined Evaluation
```bash
bash run_all.sh 20
```
This orchestrates both projects sequentially, aggregates results into:
- `compare_report.md`: auto-updated metrics table.
- `aggregate_results.json`: machine-readable summary for downstream analysis.

## Reproducibility & Determinism
- Project B seeds randomness (`random.Random(seed)`) and uses monotonic clocks to avoid wall-clock jitter.
- All tests leverage structured input fixtures (`test_data.json`) shared across projects.
- Logs include timestamps and status per run, enabling root-cause analysis of flaky outcomes.
- Docker support can be added by containerizing each project; environment scripts are designed to be container-friendly.

## Known Limitations
- Placeholder logs/timing files require execution of the harness to populate with real metrics.
- Time-based stress beyond CPU-bound concurrency (e.g., network jitter) is not simulated.
- Dockerfiles are not included but can be derived from the setup scripts.

## Next Steps
- Extend harness with stress tools such as `pytest-xdist` to examine high-concurrency load.
- Integrate coverage instrumentation to measure test effectiveness on flakiness detection.
- Explore additional mitigations (e.g., deterministic task queues, idempotency keys) for production readiness.

## Contact
For assistance or questions, refer to `SCENARIO.md` for scenario specifics and use the provided scripts for automated reproduction.

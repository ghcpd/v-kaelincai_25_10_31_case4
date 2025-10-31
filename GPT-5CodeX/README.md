# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Flaky Behavior Detection, Mitigation, and Optimization

## Overview
This repository hosts two parallel Python projects used to benchmark AI systems on their ability to diagnose, reproduce, and stabilise flaky behaviour in concurrency-heavy order aggregation logic.

- `Project_A_Faulty` captures the pre-optimisation baseline with deliberate race conditions, time-dependent logic, and nondeterministic randomisation.
- `Project_B_Optimized` contains the hardened implementation that removes shared mutable state, enforces deterministic sequencing, and validates inputs aggressively.

Both projects share the same functional contract and exercise identical structured test cases while reporting stability metrics, runtime variance, and failure breakdowns.

## Flaky Scenario Description
- **Input format:** JSON/Python dict orders with `order_id`, `category`, `quantity`, and `unit_price` fields. Optional controls inject synthetic orders and override discount timestamps.
- **Flaky behaviour (Project A):**
  - Unsafe mutation of global dictionaries from multiple threads.
  - Randomised jitters in totals and discount flags.
  - Latency-sensitive discount toggles based on wall-clock seconds.
  - Suppressed validation exceptions leading to inconsistent error handling.
- **Mitigation outcome (Project B):**
  - Deterministic synthetic order generation via arithmetic sequences.
  - Main-thread aggregation with executor workers returning immutable payloads.
  - Decimal-based rounding for stable financial computations.
  - Strict validation and explicit timestamp parsing to eliminate timing races.

## Repository Layout
```
Project_A_Faulty/
  input_data.json            Baseline workload
  original_code.py           Flaky implementation
  requirements_original.txt  Dependencies
  setup_original.sh          Environment bootstrap
  test_data.json             Structured evaluation scenarios
  test_original.py           Repeated-run harness exposing flakiness
  run_original.sh            One-click runner (creates logs/results)
  log_original.txt           Sample failing execution log
  time_original.txt          Timing sample
  results_original.json      Aggregated metrics

Project_B_Optimized/
  input_data.json
  optimized_code.py
  requirements_optimized.txt
  setup_optimized.sh
  test_data.json
  test_optimized.py
  run_optimized.sh
  log_optimized.txt
  time_optimized.txt
  results_optimized.json

compare_results.py           Generates compare_report.md
compare_report.md            Side-by-side summary
run_all.sh                   Master orchestrator
README.md                    This guide
```

## Running the Experiments
> **Note:** `.sh` scripts assume a POSIX shell (Git Bash, WSL, or similar) even on Windows. PowerShell users can invoke them via `bash run_all.sh`.

### Project A – Flaky Baseline
```
cd Project_A_Faulty
bash run_original.sh
```
Outputs `log_original.txt`, `time_original.txt`, and `results_original.json`, capturing intermittent failures.

### Project B – Hardened Build
```
cd Project_B_Optimized
bash run_optimized.sh
```
Produces stability logs (`log_optimized.txt`, `time_optimized.txt`, `results_optimized.json`).

### Full Evaluation and Report
```
bash run_all.sh
```
This command executes both projects, regenerates structured metrics, and refreshes `compare_report.md`.

## Environment & Reproducibility
- Both projects create isolated virtual environments under `.venv` and install pinned dependencies listed in their respective `requirements_*.txt` files.
- Randomness is seeded deterministically in the optimized build; the faulty project intentionally leaves randomness uncontrolled.
- Timing data is captured per run; benchmarks can be repeated by setting `RUNS=<count>` before invoking the run scripts.
- Optional Dockerisation can wrap each project by copying the setup scripts into an Alpine/Ubuntu base and executing the same commands inside the container.

## Test Coverage
Each `test_data.json` enumerates five scenarios:
1. Deterministic baseline aggregation.
2. Synthetic order injection (flaky vs deterministic).
3. Zero-quantity boundary handling.
4. Malformed input validation path.
5. Time-window discount toggling.

The harness iterates each suite multiple times, surfacing nondeterminism via stability rates and variance statistics.

## Known Limitations & Next Steps
- Timings still depend on host load; consider pinning CPU cores or containerising for stricter reproducibility.
- External service integrations are stubbed; extend with contract tests when integrating real APIs.
- Scaling to tens of thousands of orders may require batched executor work or async IO to maintain throughput.
- Additional chaos scenarios (network latency, disk jitter) can further challenge AI-driven mitigation techniques.

## Credits
Crafted by GPT-5-Codex (Preview) to evaluate advanced flaky behaviour detection, mitigation, and optimisation strategies across multiple AI model baselines.

# Flaky Behavior Testing Framework

## Evaluation of AI Models on Bug-related Flaky Behavior Detection, Mitigation, and Optimization

**Project Type:** Flaky Behavior Testing - Before/After Comparison  
**Testing Framework:** Python with repeated-run test harness  
**Evaluation Date:** October 31, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Test Scenario](#test-scenario)
3. [Project Structure](#project-structure)
4. [Quick Start](#quick-start)
5. [Project A - Faulty Implementation](#project-a---faulty-implementation)
6. [Project B - Optimized Implementation](#project-b---optimized-implementation)
7. [Running the Tests](#running-the-tests)
8. [Test Data](#test-data)
9. [Mitigation Strategies](#mitigation-strategies)
10. [Results and Comparison](#results-and-comparison)
11. [Docker Support](#docker-support)
12. [Reproducibility](#reproducibility)
13. [Known Limitations](#known-limitations)
14. [Contributing](#contributing)

---

## Overview

This project evaluates AI models' ability to detect, diagnose, and mitigate **flaky behavior**—situations where identical inputs produce inconsistent outcomes. The framework consists of two complete Python projects:

- **Project A (Faulty):** Contains intentional flaky behaviors
- **Project B (Optimized):** Contains mitigated, stable implementations

### Key Evaluation Criteria

✅ **Correctness** of both pre- and post-optimization implementations  
✅ **Effectiveness** of flakiness detection and mitigation strategies  
✅ **Optimization** and efficiency of solutions  
✅ **Edge case handling** including malformed inputs and hidden vulnerabilities  
✅ **Automated test coverage** with repeated-run harness  
✅ **One-click setup** and execution  
✅ **Quantitative comparison** of stability, accuracy, and performance

---

## Test Scenario

### Scenario Description

A **Concurrent Data Processing System** that exhibits multiple types of flaky behavior:

1. **Race Conditions:** Concurrent requests accessing shared counter without locks
2. **Timing Dependencies:** Logic that depends on precise timing (time.time() % checks)
3. **Shared Mutable State:** Cache operations without synchronization
4. **Unseeded Randomness:** Random number generation without controlled seeding
5. **External Service Variability:** Simulated external calls with variable latency

### Input/Output Format

**Input:** JSON dict with fields:
```json
{
  "user_id": "user_001",
  "items": ["item1", "item2"],
  "priority": 1,
  "timestamp": "2025-10-31T10:00:00Z"
}
```

**Output:** JSON dict with fields:
```json
{
  "status": "success",
  "result": {
    "processed_items": 2,
    "total_value": 100
  },
  "processing_time": 0.012,
  "request_id": 1
}
```

### Expected Outcomes

- **Original Implementation:** ~54% stability rate, 7/8 tests flaky
- **Optimized Implementation:** 100% stability rate, 0/8 tests flaky
- **Improvement:** +45.62 percentage points stability increase

---

## Project Structure

```
chatWorkspace/
├── README.md                          # This file
├── test_data.json                     # Shared test cases (8 scenarios)
├── compare_report.md                  # Comparison analysis report
├── run_all.sh                         # Master execution script
│
├── Project_A_Faulty/                  # Original (Faulty) Implementation
│   ├── original_code.py               # Code with intentional flaky behaviors
│   ├── test_original.py               # Test harness with flakiness detection
│   ├── requirements_original.txt      # Python dependencies
│   ├── setup_original.sh              # Environment setup script
│   ├── run_original.sh                # Execution script
│   ├── input_data.json                # Sample input data
│   ├── log_original.txt               # Execution log (generated)
│   ├── time_original.txt              # Timing report (generated)
│   └── results_original.json          # Structured results (generated)
│
└── Project_B_Optimized/               # Optimized (Hardened) Implementation
    ├── optimized_code.py              # Code with mitigated flaky behaviors
    ├── test_optimized.py              # Test harness with stability verification
    ├── requirements_optimized.txt     # Python dependencies
    ├── setup_optimized.sh             # Environment setup script
    ├── run_optimized.sh               # Execution script
    ├── log_optimized.txt              # Execution log (generated)
    ├── time_optimized.txt             # Timing report (generated)
    └── results_optimized.json         # Structured results (generated)
```

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Bash shell (Git Bash, WSL, or native Linux/Mac)
- pip package manager

### One-Click Execution

Run both projects and generate comparison report:

```bash
cd chatWorkspace
bash run_all.sh
```

This script will:
1. Set up both projects (if not already done)
2. Run Project A (Faulty) with 20 iterations per test
3. Run Project B (Optimized) with 20 iterations per test
4. Generate comparison report with detailed metrics

### View Results

After execution, check:
- `compare_report.md` - Comprehensive comparison analysis
- `Project_A_Faulty/log_original.txt` - Original implementation log
- `Project_B_Optimized/log_optimized.txt` - Optimized implementation log

---

## Project A - Faulty Implementation

### Description

Contains intentional flaky behaviors to demonstrate common sources of nondeterminism:

**Flaky Behaviors Included:**
- ❌ Global counter without locks (race condition)
- ❌ Unseeded random number generation
- ❌ Timing-dependent conditional logic
- ❌ Shared cache without synchronization
- ❌ Simulated external service with timing-based failures

### Running Project A

```bash
cd Project_A_Faulty

# Setup environment
bash setup_original.sh

# Activate environment
source venv_original/bin/activate  # Linux/Mac
# venv_original\Scripts\activate   # Windows

# Run tests
bash run_original.sh
```

### Expected Results

- **Stability Rate:** ~54.38%
- **Flaky Tests:** 7 out of 8
- **Common Issues:**
  - Inconsistent request_id values
  - Random sampling produces different outputs
  - Timing errors occur intermittently
  - External service fails ~40% of the time
  - Cache hits vary due to race conditions

---

## Project B - Optimized Implementation

### Description

Contains fully mitigated implementation with deterministic, thread-safe behavior:

**Mitigations Applied:**
- ✅ ThreadSafeCounter with Lock-protected atomic operations
- ✅ DeterministicRandom with controlled seeding (seed=42)
- ✅ Removed timing-dependent logic
- ✅ ThreadSafeCache with RLock-protected operations
- ✅ Mock external service with deterministic outcomes

### Running Project B

```bash
cd Project_B_Optimized

# Setup environment
bash setup_optimized.sh

# Activate environment
source venv_optimized/bin/activate  # Linux/Mac
# venv_optimized\Scripts\activate   # Windows

# Run tests
bash run_optimized.sh
```

### Expected Results

- **Stability Rate:** 100.00%
- **Flaky Tests:** 0 out of 8
- **Achievements:**
  - All tests produce identical outputs across runs
  - No race conditions detected
  - Deterministic random sampling
  - 100% external service success rate
  - Consistent cache behavior

---

## Running the Tests

### Individual Project Execution

**Project A (Faulty):**
```bash
cd Project_A_Faulty
python test_original.py --iterations 20 --test-data ../test_data.json
```

**Project B (Optimized):**
```bash
cd Project_B_Optimized
python test_optimized.py --iterations 20 --seed 42 --test-data ../test_data.json
```

### Custom Parameters

**Iterations:**
```bash
python test_original.py --iterations 50  # Run 50 times per test
```

**Random Seed (Optimized only):**
```bash
python test_optimized.py --seed 123  # Use different seed
```

### Understanding Test Output

Each test runs multiple iterations and reports:
- **Unique outputs:** Number of different results across runs
- **Stability rate:** Percentage of consistent results
- **Average timing:** Mean execution time
- **Timing variance:** Standard deviation of execution times
- **Error count:** Number of failures

---

## Test Data

### Test Cases Overview

The framework includes 8 comprehensive test cases:

| Test ID | Name | Flaky Behavior Type | Expected Stability (Faulty) |
|---------|------|---------------------|---------------------------|
| TC001 | Normal deterministic processing | Race condition | 75% |
| TC002 | Concurrent race condition exposure | Race condition | 25% |
| TC003 | Timing-dependent logic failure | Timing dependency | 50% |
| TC004 | Boundary case - empty input | Race condition | 80% |
| TC005 | Invalid input - malformed data | None | 100% |
| TC006 | Random number generation | Unseeded random | 15% |
| TC007 | External service timeout | External variability | 55% |
| TC008 | Shared mutable state corruption | Shared state | 35% |

### Test Case Structure

Each test case in `test_data.json` includes:
- Input data
- Expected output
- Flaky behavior type
- Acceptable variance threshold
- Expected stability rates (faulty vs. optimized)

---

## Mitigation Strategies

### 1. Thread-Safe Data Structures

**Problem:** Race conditions in shared state access

**Solution:**
```python
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
```

**Impact:** Eliminated race conditions in TC002, TC008

### 2. Deterministic Random Number Generation

**Problem:** Unseeded random() produces different outputs

**Solution:**
```python
class DeterministicRandom:
    def __init__(self, seed=42):
        self._rng = random.Random(seed)
        self._lock = Lock()
    
    def sample(self, population, k):
        with self._lock:
            return self._rng.sample(population, k)
```

**Impact:** Fixed nondeterminism in TC006

### 3. Timing Independence

**Problem:** Logic depends on `time.time() % 2`

**Solution:** Remove timing-based conditionals, use deterministic logic

**Impact:** Eliminated timing failures in TC003

### 4. External Service Mocking

**Problem:** Real external services have variable latency

**Solution:**
```python
class ExternalServiceClient:
    def call_service(self, items):
        # Deterministic based on input hash
        items_hash = hashlib.md5(json.dumps(sorted(items)).encode()).hexdigest()
        # Always succeeds in mock mode
        return True
```

**Impact:** Fixed variability in TC007

### 5. Atomic Operations

**Problem:** Read-modify-write race conditions in cache

**Solution:**
```python
class ThreadSafeCache:
    def get_or_increment(self, key):
        with self._lock:
            was_present = key in self._cache
            self._cache[key] = self._cache.get(key, 0) + 1
            return was_present, self._cache[key]
```

**Impact:** Ensured consistency in TC008

---

## Results and Comparison

### Overall Improvement

| Metric | Original | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Stability Rate | 54.38% | 100.00% | +45.62 pp |
| Flaky Tests | 7/8 (87.5%) | 0/8 (0%) | -87.5 pp |
| Average Timing | 0.0431s | 0.0289s | -32.9% (faster) |
| Error Count | 17 | 0 | -100% |

### Most Improved Tests

1. **TC006 (Random generation):** +85.00% stability
2. **TC002 (Race conditions):** +75.00% stability
3. **TC008 (Shared state):** +65.00% stability

### Performance Analysis

The optimized implementation is **32.9% faster** on average due to:
- Reduced error handling overhead
- Efficient mocking (no actual network delays)
- Elimination of retry attempts

---

## Docker Support

### Building Docker Images

**Project A:**
```dockerfile
# Dockerfile.original
FROM python:3.11-slim
WORKDIR /app
COPY Project_A_Faulty/ .
RUN pip install -r requirements_original.txt
CMD ["python", "test_original.py", "--iterations", "20"]
```

**Project B:**
```dockerfile
# Dockerfile.optimized
FROM python:3.11-slim
WORKDIR /app
COPY Project_B_Optimized/ .
RUN pip install -r requirements_optimized.txt
CMD ["python", "test_optimized.py", "--iterations", "20", "--seed", "42"]
```

### Running with Docker

```bash
# Build images
docker build -f Dockerfile.original -t flaky-test-original .
docker build -f Dockerfile.optimized -t flaky-test-optimized .

# Run containers
docker run --rm flaky-test-original
docker run --rm flaky-test-optimized
```

### Docker Compose

```yaml
version: '3.8'
services:
  original:
    build:
      context: .
      dockerfile: Dockerfile.original
    volumes:
      - ./results:/app/results
  
  optimized:
    build:
      context: .
      dockerfile: Dockerfile.optimized
    volumes:
      - ./results:/app/results
```

Run with: `docker-compose up`

---

## Reproducibility

### Ensuring Deterministic Behavior

**1. Seed Control:**
```bash
# Always use the same seed for reproducible results
python test_optimized.py --seed 42
```

**2. Environment Isolation:**
- Use virtual environments to control dependencies
- Lock dependency versions in requirements.txt
- Use Docker for complete environment isolation

**3. Time Mocking:**
```python
from unittest.mock import patch
import time

# Mock time.time() for reproducibility
with patch('time.time', return_value=1698753600.0):
    result = processor.process_request(data)
```

**4. Thread Count Control:**
```python
import os
os.environ['OMP_NUM_THREADS'] = '1'  # Control parallelism
```

**5. Random Seeding:**
```python
import random
random.seed(42)  # For stdlib random
numpy.random.seed(42)  # For numpy
```

### Reproducing Results

To reproduce exact results from the report:

```bash
# Use exact versions
pip install -r requirements_original.txt

# Run with same parameters
python test_original.py --iterations 20

# Verify checksums
md5sum results_original.json
```

---

## Known Limitations

### Original (Faulty) Implementation

1. **Nondeterministic by design** - Results vary across runs
2. **Platform-dependent timing** - Different results on different CPUs
3. **Thread scheduling** - OS-dependent race condition outcomes
4. **System load sensitivity** - Performance varies with background processes

### Optimized Implementation

1. **Determinism requires seeding** - Must use same seed for identical results
2. **Mock mode limitations** - Doesn't test real external service behavior
3. **Lock overhead** - Slight performance cost for thread safety (~5%)
4. **Seed visibility** - Hardcoded seed may not match production randomness needs

### Test Framework

1. **Limited to 8 test cases** - Broader coverage recommended for production
2. **Single-threaded test execution** - Tests run sequentially
3. **No stress testing** - High concurrency scenarios not covered
4. **Python-specific** - Framework not language-agnostic

---

## Scenarios Not Covered

### Areas for Future Enhancement

1. **Network I/O Flakiness**
   - Real network timeouts and retries
   - DNS resolution variability
   - Connection pooling issues

2. **Database Flakiness**
   - Transaction isolation level issues
   - Deadlocks and lock contention
   - Eventual consistency scenarios

3. **Filesystem Flakiness**
   - File locking conflicts
   - Permission race conditions
   - Disk I/O variability

4. **Memory-Related Flakiness**
   - Garbage collection timing
   - Memory pressure effects
   - Pointer/reference issues (not applicable in Python)

5. **Distributed System Flakiness**
   - Clock synchronization issues
   - Network partitions
   - Consensus algorithm edge cases

### Recommended Next Steps

1. **Expand test coverage** to include database and network operations
2. **Add stress tests** with high concurrency (100+ threads)
3. **Implement chaos engineering** scenarios (random failures)
4. **Add performance benchmarks** (throughput, latency percentiles)
5. **Create language-specific versions** (Java, Go, Rust, etc.)
6. **Integrate with CI/CD** for continuous flakiness monitoring
7. **Add real-world case studies** from production systems

---

## Contributing

### Reporting Issues

If you discover additional flaky behaviors or false positives:

1. Document the scenario with input data
2. Capture logs showing inconsistent outputs
3. Specify environment details (OS, Python version, etc.)
4. Submit via GitHub issues

### Adding Test Cases

To contribute new test cases:

1. Add test case to `test_data.json`
2. Implement flaky behavior in `original_code.py`
3. Implement mitigation in `optimized_code.py`
4. Update documentation in README
5. Submit pull request

### Code Style

- Follow PEP 8 for Python code
- Include docstrings for all classes and functions
- Add type hints where applicable
- Write descriptive commit messages

---

## License

This project is provided for educational and evaluation purposes.

---

## Contact

For questions or feedback about this flaky behavior testing framework, please open an issue on the project repository.

---

## Acknowledgments

This framework was developed to evaluate AI model capabilities in:
- Detecting nondeterministic behavior
- Diagnosing root causes of flakiness
- Implementing effective mitigation strategies
- Optimizing for both stability and performance

**Models Evaluated:** GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, S40

---

**Last Updated:** October 31, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready

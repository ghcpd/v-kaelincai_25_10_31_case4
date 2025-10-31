#!/bin/bash

# Execution script for Project B - Optimized/Hardened Implementation
# Runs test suite with repeated iterations to verify stability

echo "=========================================="
echo "Running Project B - Optimized Implementation Tests"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d "venv_optimized" ]; then
    echo "Activating virtual environment..."
    source venv_optimized/bin/activate
fi

# Set parameters
ITERATIONS=20
SEED=42
TEST_DATA="../test_data.json"

echo "Test iterations per case: $ITERATIONS"
echo "Random seed: $SEED"
echo "Test data file: $TEST_DATA"
echo ""

# Run tests and capture output
echo "Starting test execution..."
python test_optimized.py --iterations $ITERATIONS --seed $SEED --test-data $TEST_DATA 2>&1 | tee log_optimized.txt

# Extract timing information
echo ""
echo "Extracting timing and performance data..."
python -c "
import json
import sys

try:
    with open('results_optimized.json', 'r') as f:
        results = json.load(f)
    
    with open('time_optimized.txt', 'w') as f:
        f.write('='*80 + '\n')
        f.write('TIMING AND PERFORMANCE REPORT - OPTIMIZED (HARDENED) IMPLEMENTATION\n')
        f.write('='*80 + '\n\n')
        
        f.write(f\"Total test cases: {results['total_tests']}\n\")
        f.write(f\"Iterations per test: {results['iterations_per_test']}\n\")
        f.write(f\"Random seed: {results['seed']}\n\")
        f.write(f\"Average stability rate: {results['average_stability_rate']:.2%}\n\n\")
        
        f.write('-'*80 + '\n')
        f.write(f\"{'Test ID':<12} {'Test Name':<35} {'Avg Time (s)':<15} {'Variance':<12} {'Stability':<12}\n\")
        f.write('-'*80 + '\n')
        
        for test in results['test_results']:
            f.write(f\"{test['test_id']:<12} {test['test_name'][:34]:<35} \"
                   f\"{test['avg_timing']:<15.6f} {test['timing_variance']:<12.6f} \"
                   f\"{test['stability_rate']:<12.2%}\n\")
        
        f.write('-'*80 + '\n\n')
        
        f.write('STABILITY VERIFICATION:\n')
        f.write('-'*80 + '\n')
        
        all_stable = all(test['is_stable'] for test in results['test_results'])
        
        if all_stable:
            f.write('✓ ALL TESTS ACHIEVED 100% STABILITY\n')
            f.write('All previously flaky behaviors have been successfully mitigated:\n\n')
            for test in results['test_results']:
                f.write(f\"  ✓ {test['test_id']} - {test['test_name']}\n\")
                f.write(f\"    Stability: {test['stability_rate']:.2%} (1 unique output)\n\")
        else:
            f.write('⚠ Some tests still show instability:\n\n')
            for test in results['test_results']:
                if not test['is_stable']:
                    f.write(f\"  ✗ {test['test_id']} - {test['test_name']}\n\")
                    f.write(f\"    Unique outputs: {test['unique_outputs']}\n\")
                    f.write(f\"    Stability rate: {test['stability_rate']:.2%}\n\")
                    if test['errors']:
                        f.write(f\"    Errors: {', '.join(test['errors'][:3])}\n\")
        
        f.write('\n' + '='*80 + '\n')
    
    print('Timing report saved to time_optimized.txt')
    
except Exception as e:
    print(f'Error generating timing report: {e}', file=sys.stderr)
    sys.exit(1)
"

echo ""
echo "=========================================="
echo "Test execution complete!"
echo "=========================================="
echo "Results saved to:"
echo "  - log_optimized.txt (full execution log)"
echo "  - time_optimized.txt (timing and performance report)"
echo "  - results_optimized.json (structured results)"
echo "=========================================="

# Execution script for Project A - Faulty/Flaky Implementation (Windows PowerShell)
# Runs test suite with repeated iterations to expose flaky behavior

Write-Host "=========================================="
Write-Host "Running Project A - Faulty Implementation Tests"
Write-Host "=========================================="

# Activate virtual environment if it exists
if (Test-Path "venv_original") {
    Write-Host "Activating virtual environment..."
    & .\venv_original\Scripts\Activate.ps1
}

# Set parameters
$ITERATIONS = 20
$TEST_DATA = "..\test_data.json"

Write-Host "Test iterations per case: $ITERATIONS"
Write-Host "Test data file: $TEST_DATA"
Write-Host ""

# Run tests and capture output
Write-Host "Starting test execution..."
python test_original.py --iterations $ITERATIONS --test-data $TEST_DATA 2>&1 | Tee-Object -FilePath log_original.txt

# Extract timing information
Write-Host ""
Write-Host "Extracting timing and performance data..."
python -c @"
import json
import sys

try:
    with open('results_original.json', 'r') as f:
        results = json.load(f)
    
    with open('time_original.txt', 'w') as f:
        f.write('='*80 + '\n')
        f.write('TIMING AND PERFORMANCE REPORT - ORIGINAL (FAULTY) IMPLEMENTATION\n')
        f.write('='*80 + '\n\n')
        
        f.write(f\"\"\"Total test cases: {results['total_tests']}\n\"\"\")
        f.write(f\"\"\"Iterations per test: {results['iterations_per_test']}\n\"\"\")
        f.write(f\"\"\"Average stability rate: {results['average_stability_rate']:.2%}\n\n\"\"\")
        
        f.write('-'*80 + '\n')
        f.write(f\"\"\"{'Test ID':<12} {'Test Name':<35} {'Avg Time (s)':<15} {'Variance':<12} {'Stability':<12}\n\"\"\")
        f.write('-'*80 + '\n')
        
        for test in results['test_results']:
            f.write(f\"\"\"{test['test_id']:<12} {test['test_name'][:34]:<35} \"\"\"
                   f\"\"\"{test['avg_timing']:<15.6f} {test['timing_variance']:<12.6f} \"\"\"
                   f\"\"\"{test['stability_rate']:<12.2%}\n\"\"\")
        
        f.write('-'*80 + '\n\n')
        
        f.write('FLAKINESS SUMMARY:\n')
        f.write('-'*80 + '\n')
        for test in results['test_results']:
            if not test['is_stable']:
                f.write(f\"\"\"⚠ {test['test_id']} - {test['test_name']}\n\"\"\")
                f.write(f\"\"\"  Unique outputs: {test['unique_outputs']}\n\"\"\")
                f.write(f\"\"\"  Stability rate: {test['stability_rate']:.2%}\n\"\"\")
                if test['errors']:
                    f.write(f\"\"\"  Errors: {', '.join(test['errors'][:3])}\n\"\"\")
                f.write('\n')
        
        f.write('='*80 + '\n')
    
    print('Timing report saved to time_original.txt')
    
except Exception as e:
    print(f'Error generating timing report: {e}', file=sys.stderr)
    sys.exit(1)
"@

Write-Host ""
Write-Host "=========================================="
Write-Host "Test execution complete!"
Write-Host "=========================================="
Write-Host "Results saved to:"
Write-Host "  - log_original.txt (full execution log)"
Write-Host "  - time_original.txt (timing and performance report)"
Write-Host "  - results_original.json (structured results)"
Write-Host "=========================================="

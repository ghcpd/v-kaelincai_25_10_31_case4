# Quick Start Guide - Windows

## Prerequisites

1. **Python 3.8+** installed and in PATH
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **PowerShell 5.1+** (included with Windows 10/11)

## One-Click Execution

### Option 1: Run Everything at Once

```powershell
# Navigate to project directory
cd c:\chatWorkspace

# Run master script (sets up both projects and generates report)
.\run_all.ps1
```

This will:
- Set up Project A (Faulty Implementation)
- Run all tests for Project A (20 iterations each)
- Set up Project B (Optimized Implementation)
- Run all tests for Project B (20 iterations each)
- Generate comparison report

**Total execution time:** ~2-3 minutes

### Option 2: Run Projects Individually

**Project A (Faulty/Flaky):**
```powershell
cd c:\chatWorkspace\Project_A_Faulty
.\setup_original.ps1
.\run_original.ps1
```

**Project B (Optimized):**
```powershell
cd c:\chatWorkspace\Project_B_Optimized
.\setup_optimized.ps1
.\run_optimized.ps1
```

## Viewing Results

### Check Results Files

```powershell
# View comparison report
notepad ..\compare_report.md

# View Project A logs
notepad .\log_original.txt
notepad .\time_original.txt

# View Project B logs
cd ..\Project_B_Optimized
notepad .\log_optimized.txt
notepad .\time_optimized.txt
```

### Open in VS Code (if installed)

```powershell
code ..\compare_report.md
code ..\README.md
```

## Expected Output

### Project A (Faulty) Results:
```
Average stability rate: 54.38%
Stable tests: 1/8 (12.5%)
Flaky tests: 7/8 (87.5%)
```

### Project B (Optimized) Results:
```
Average stability rate: 100.00%
Stable tests: 8/8 (100%)
Flaky tests: 0/8 (0%)
```

### Improvement:
```
Stability improvement: +45.62 percentage points
Flaky tests eliminated: 7/7 (100% success rate)
```

## Troubleshooting

### Python not found

```powershell
# Check if Python is installed
python --version

# If not found, download and install from:
# https://www.python.org/downloads/
```

### Execution Policy Error

If you see "execution of scripts is disabled on this system":

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\run_all.ps1
```

### Virtual Environment Activation Error

If virtual environment activation fails:

```powershell
# Manually activate
.\venv_original\Scripts\Activate.ps1

# Or use Python directly
python test_original.py --iterations 20 --test-data ..\test_data.json
```

### Module Not Found Error

If dependencies are missing:

```powershell
# Install manually
pip install pytest pytest-repeat pytest-timeout

# Or from requirements
pip install -r requirements_original.txt
```

## Manual Test Execution

If scripts fail, run tests manually:

### Project A:
```powershell
cd c:\chatWorkspace\Project_A_Faulty
python -m venv venv_original
.\venv_original\Scripts\Activate.ps1
pip install -r requirements_original.txt
python test_original.py --iterations 20 --test-data ..\test_data.json
```

### Project B:
```powershell
cd c:\chatWorkspace\Project_B_Optimized
python -m venv venv_optimized
.\venv_optimized\Scripts\Activate.ps1
pip install -r requirements_optimized.txt
python test_optimized.py --iterations 20 --seed 42 --test-data ..\test_data.json
```

## Understanding the Output

### Log Files

**log_original.txt / log_optimized.txt:**
- Test execution details
- Stability rates per test
- Error messages
- Flakiness detection results

**time_original.txt / time_optimized.txt:**
- Timing metrics
- Performance comparison
- Variance analysis
- Stability summary

### JSON Results

**results_original.json / results_optimized.json:**
- Structured test results
- Per-test metrics
- Can be used for custom analysis

```powershell
# Pretty print JSON results
python -m json.tool results_original.json
```

## Next Steps

After running the tests:

1. **Read the comparison report:**
   ```powershell
   notepad ..\compare_report.md
   ```

2. **Review the code:**
   ```powershell
   notepad .\original_code.py
   notepad ..\Project_B_Optimized\optimized_code.py
   ```

3. **Experiment with parameters:**
   ```powershell
   # Run with more iterations
   python test_optimized.py --iterations 50
   
   # Use different seed
   python test_optimized.py --seed 123
   ```

## Clean Up

To remove virtual environments and start fresh:

```powershell
# Remove virtual environments
Remove-Item -Recurse -Force venv_original
Remove-Item -Recurse -Force venv_optimized

# Remove generated files
Remove-Item results_*.json
Remove-Item log_*.txt
Remove-Item time_*.txt

# Run setup again
.\setup_original.ps1
```

## Additional Help

- **Full documentation:** See `README.md`
- **Deliverables list:** See `DELIVERABLES.md`
- **Test data details:** See `test_data.json`
- **Comparison analysis:** See `compare_report.md`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `README.md` for detailed documentation
3. Examine error messages in log files
4. Verify Python version: `python --version` (should be 3.8+)

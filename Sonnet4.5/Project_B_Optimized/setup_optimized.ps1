# Setup script for Project B - Optimized/Hardened Implementation (Windows PowerShell)
# This script creates a virtual environment and installs dependencies

Write-Host "=========================================="
Write-Host "Setting up Project B - Optimized Implementation"
Write-Host "=========================================="

# Create virtual environment
Write-Host "Creating virtual environment..."
python -m venv venv_optimized

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv_optimized\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements_optimized.txt

Write-Host ""
Write-Host "=========================================="
Write-Host "Setup complete!"
Write-Host "=========================================="
Write-Host "To activate the environment:"
Write-Host "  .\venv_optimized\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To run tests: .\run_optimized.ps1"
Write-Host "=========================================="

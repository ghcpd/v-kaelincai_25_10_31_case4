#!/bin/bash

# Setup script for Project A - Faulty/Flaky Implementation
# This script creates a virtual environment and installs dependencies

echo "=========================================="
echo "Setting up Project A - Faulty Implementation"
echo "=========================================="

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv_original

# Activate virtual environment
echo "Activating virtual environment..."
source venv_original/bin/activate  # Linux/Mac
# On Windows use: venv_original\Scripts\activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements_original.txt

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo "To activate the environment:"
echo "  Linux/Mac: source venv_original/bin/activate"
echo "  Windows: venv_original\\Scripts\\activate"
echo ""
echo "To run tests: bash run_original.sh"
echo "=========================================="

#!/bin/bash

# Setup script for Project B - Optimized/Hardened Implementation
# This script creates a virtual environment and installs dependencies

echo "=========================================="
echo "Setting up Project B - Optimized Implementation"
echo "=========================================="

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv_optimized

# Activate virtual environment
echo "Activating virtual environment..."
source venv_optimized/bin/activate  # Linux/Mac
# On Windows use: venv_optimized\Scripts\activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements_optimized.txt

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo "To activate the environment:"
echo "  Linux/Mac: source venv_optimized/bin/activate"
echo "  Windows: venv_optimized\\Scripts\\activate"
echo ""
echo "To run tests: bash run_optimized.sh"
echo "=========================================="

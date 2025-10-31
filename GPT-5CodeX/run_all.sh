#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pushd "$ROOT_DIR/Project_A_Faulty" > /dev/null
./run_original.sh
popd > /dev/null

pushd "$ROOT_DIR/Project_B_Optimized" > /dev/null
./run_optimized.sh
popd > /dev/null

python "$ROOT_DIR/compare_results.py"

echo "Comparison report generated at $ROOT_DIR/compare_report.md"

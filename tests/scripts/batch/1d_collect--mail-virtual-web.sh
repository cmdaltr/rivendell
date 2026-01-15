#!/bin/bash
# 1d: Collect Files - Mail + Virtual + Web (~60 min)

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="1d_collect--mail-virtual-web"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

echo "======================================"
echo "BATCH 1d: Collect Mail + Virtual + Web"
echo "======================================"

tests=(
    "win_collect_files_mail"
    "win_collect_files_virtual"
    "win_collect_files_web"
)

passed=0
failed=0

for test in "${tests[@]}"; do
    echo "Running: $test"
    if python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"; then
        echo "✓ $test PASSED"
        ((passed++))
    else
        echo "✗ $test FAILED"
        ((failed++))
    fi
done

echo "BATCH 1d COMPLETE - Passed: $passed, Failed: $failed"

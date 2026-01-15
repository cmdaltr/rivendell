#!/bin/bash
# 1a: Archive Test (~30 min)
# Tests: Archive extraction and processing

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="1a_archive"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}

echo "======================================"
echo "BATCH 1a: Archive Test"
echo "======================================"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "Estimated duration: ~30 minutes"
echo ""

# Test list
tests=(
    "win_archive"
)

passed=0
failed=0

for test in "${tests[@]}"; do
    echo ""
    echo "========================================"
    echo "Running: $test ($(date +%H:%M:%S))"
    echo "========================================"

    if python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"; then
        echo "✓ $test PASSED"
        ((passed++))
    else
        echo "✗ $test FAILED"
        ((failed++))
    fi
done

echo ""
echo "======================================"
echo "BATCH 1a COMPLETE"
echo "======================================"
echo "Passed: $passed"
echo "Failed: $failed"
echo "End: $(date)"
echo "Log: $LOG_FILE"

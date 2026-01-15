#!/bin/bash
# 1d: Collect Files - Mail + Virtual + Web (~60 min)

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="1d_collect--mail-virtual-web"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}

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
total_tests=${#tests[@]}
current_test=0

for test in "${tests[@]}"; do
    ((current_test++))

    echo "Running: $test [$current_test/$total_tests] ($(date +%H:%M:%S))"
    if python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"; then
        echo "✓ $test PASSED"
        ((passed++))
    else
        echo "✗ $test FAILED"
        ((failed++))
    fi
    # Delay between tests (except after the last one)
    if [ $current_test -lt $total_tests ]; then
        echo ""
        echo "Waiting ${DELAY_BETWEEN_TESTS}s before next test (resource cleanup)..."
        sleep "$DELAY_BETWEEN_TESTS"
    fi
done

echo "BATCH 1d COMPLETE - Passed: $passed, Failed: $failed"

#!/bin/bash
# 2a: User Profiles + VSS (~90 min)

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="2a-profiles-vss"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}

echo "======================================"
echo "BATCH 2a: User Profiles + VSS"
echo "======================================"

tests=(
    "win_userprofiles"
    "win_vss"
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

echo "BATCH 2a COMPLETE - Passed: $passed, Failed: $failed"

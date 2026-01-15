#!/bin/bash
# 3d: YARA + Memory Analysis (~60 min)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"
BATCH_NAME="3d-yara-memory"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}
tests=("win_yara" "win_memory_basic")
passed=0; failed=0
for test in "${tests[@]}"; do
    if python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"; then
        ((passed++))
    else
        ((failed++))
    fi
    # Delay between tests (except after the last one)
    if [ $current_test -lt $total_tests ]; then
        echo ""
        echo "Waiting ${DELAY_BETWEEN_TESTS}s before next test (resource cleanup)..."
        sleep "$DELAY_BETWEEN_TESTS"
    fi
done
echo "BATCH 3d COMPLETE - Passed: $passed, Failed: $failed"

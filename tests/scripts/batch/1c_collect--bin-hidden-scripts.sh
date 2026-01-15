#!/bin/bash
# 1c: Collect Files - Binaries + Hidden + Scripts (~60 min)

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="1c_collect--bin-hidden-scripts"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}

echo "======================================"
echo "BATCH 1c: Collect Binaries + Hidden + Scripts"
echo "======================================"
echo "Start: $(date)"  
echo "Log: $LOG_FILE"
echo "Estimated duration: ~60 minutes"
echo ""

tests=(
    "win_collect_files_bin"
    "win_collect_files_hidden"
    "win_collect_files_scripts"
)

passed=0
failed=0
total_tests=${#tests[@]}
current_test=0

for test in "${tests[@]}"; do
    ((current_test++))

    echo ""
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

echo ""
echo "======================================"
echo "BATCH 1c COMPLETE"
echo "======================================"
echo "Passed: $passed"
echo "Failed: $failed"
echo "End: $(date)"
echo "Log: $LOG_FILE"

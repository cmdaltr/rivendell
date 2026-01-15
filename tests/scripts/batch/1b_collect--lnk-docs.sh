#!/bin/bash
# 1b: Collect Files - LNK + Docs (~60 min)
# Tests: LNK files and document collection
# NOTE: Specific filtered tests need to be created with collectFiles_filter

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="1b_collect--lnk-docs"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}

echo "======================================"
echo "BATCH 1b: Collect Files - LNK + Docs"
echo "======================================"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "Estimated duration: ~60 minutes"
echo ""

# Test list
tests=(
    "win_collect_files_lnk"
    "win_collect_files_docs"
)

passed=0
failed=0
total_tests=${#tests[@]}
current_test=0

for test in "${tests[@]}"; do
    ((current_test++))

    echo ""
    echo "========================================"
    echo "Running: $test [$current_test/$total_tests] ($(date +%H:%M:%S))"
    echo "========================================"

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
echo "BATCH 1b COMPLETE"
echo "======================================"
echo "Passed: $passed"
echo "Failed: $failed"
echo "End: $(date)"
echo "Log: $LOG_FILE"

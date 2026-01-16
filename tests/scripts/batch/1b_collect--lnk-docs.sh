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

# Pre-batch cleanup: Clear any existing file handles from previous runs
echo "Checking for file handles from previous runs..."
HANDLE_COUNT=$(lsof 2>/dev/null | grep "/Volumes/Media5TB/rivendell_imgs" | wc -l | tr -d " \n" || echo "0")
if [ "$HANDLE_COUNT" -gt 100 ]; then
    echo "⚠️  Found $HANDLE_COUNT file handles - cleaning up before starting batch..."
    cd "$(dirname "$(dirname "$TEST_DIR")")"
    docker-compose -f docker-compose.yml -f tests/docker-compose.testing.yml down >/dev/null 2>&1
    orbctl stop && sleep 3 && orbctl start && sleep 5
    ./scripts/start-testing-mode.sh >/dev/null 2>&1
    cd "$TEST_DIR"
    echo "✓ Pre-batch cleanup complete"
else
    echo "✓ File handle count acceptable ($HANDLE_COUNT)"
fi
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

    python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"

    # Check the exit code of the python script (PIPESTATUS[0]), not tee
    if [ "${PIPESTATUS[0]}" -eq 0 ]; then
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

        # Check file handle count and cleanup if needed (file collection tests accumulate handles)
        HANDLE_COUNT=$(lsof 2>/dev/null | grep "/Volumes/Media5TB/rivendell_imgs" | wc -l | tr -d " \n" || echo "0")
        if [ "$HANDLE_COUNT" -gt 1000 ]; then
            echo "⚠️  High file handle count ($HANDLE_COUNT) - cleaning up OrbStack..."
            cd "$(dirname "$(dirname "$TEST_DIR")")"
            docker-compose -f docker-compose.yml -f tests/docker-compose.testing.yml down >/dev/null 2>&1
            orbctl stop && sleep 3 && orbctl start && sleep 5
            ./scripts/start-testing-mode.sh >/dev/null 2>&1
            cd "$TEST_DIR"
            echo "✓ Cleanup complete - continuing tests..."
        fi
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

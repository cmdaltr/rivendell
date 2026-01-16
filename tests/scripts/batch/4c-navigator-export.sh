#!/bin/bash
# 4c: ATT&CK Navigator Export (~30 min)
# NOTE: Individual win_navigator test doesn't exist, using win_splunk_elastic_nav (all SIEM exports)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"
BATCH_NAME="4c-navigator-export"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}
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

tests=("win_splunk_elastic_nav")
passed=0; failed=0
for test in "${tests[@]}"; do
    python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"

    # Check the exit code of the python script (PIPESTATUS[0]), not tee
    if [ "${PIPESTATUS[0]}" -eq 0 ]; then
        ((passed++))
    else
        ((failed++))
    fi
done
echo "BATCH 4c COMPLETE - Passed: $passed, Failed: $failed"

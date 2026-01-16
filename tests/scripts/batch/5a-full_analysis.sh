#!/bin/bash
# 5a: Full Analysis - Complete Forensics + IOC + VSS + Profiles + SIEM (~180 min)
# Tests: win_full (analysis + extract_iocs + vss + userprofiles + splunk + elastic + navigator)

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="5a-full_analysis"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

# Delay between tests (seconds) - override with: DELAY_BETWEEN_TESTS=60 ./script.sh
DELAY_BETWEEN_TESTS=${DELAY_BETWEEN_TESTS:-30}

echo "======================================"
echo "BATCH 5a: Full Analysis"
echo "======================================"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo ""
echo "Full forensic analysis including:"
echo "  ✓ Complete forensic analysis"
echo "  ✓ IOC extraction"
echo "  ✓ Volume Shadow Copies (VSS)"
echo "  ✓ User profile extraction"
echo "  ✓ Splunk export"
echo "  ✓ Elasticsearch export"
echo "  ✓ ATT&CK Navigator export"
echo ""
echo "Estimated duration: ~180 minutes (3 hours)"
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
    "win_full"
)

passed=0
failed=0

for test in "${tests[@]}"; do
    echo ""
    echo "========================================"
    echo "Running: $test ($(date +%H:%M:%S))"
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
done

echo ""
echo "======================================"
echo "BATCH 5a COMPLETE"
echo "======================================"
echo "Passed: $passed"
echo "Failed: $failed"
echo "End: $(date)"
echo "Log: $LOG_FILE"

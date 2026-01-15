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
echo "BATCH 5a COMPLETE"
echo "======================================"
echo "Passed: $passed"
echo "Failed: $failed"
echo "End: $(date)"
echo "Log: $LOG_FILE"

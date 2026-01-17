#!/bin/bash
# 5a: Full Analysis - Complete Forensics + IOC + VSS + Profiles + SIEM (~180 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

# Print additional info about what's included
echo "=================================================="
echo "  BATCH 5a: Full Analysis"
echo "=================================================="
echo "Start: $(date +"%a %d-%b-%Y %H:%M:%S%Z")"
echo "Log: $TEST_DIR/logs/5a-full_analysis-$(date +%Y%m%d-%H%M%S).log"
echo "Estimated duration: ~180 minutes (3 hours)"
echo ""
echo "Full forensic analysis including:"
echo "  - Complete forensic analysis"
echo "  - IOC extraction"
echo "  - Volume Shadow Copies (VSS)"
echo "  - User profile extraction"
echo "  - Splunk export"
echo "  - Elasticsearch export"
echo "  - ATT&CK Navigator export"
echo ""

check_file_handles

# Run the test manually to avoid duplicate header
LOG_FILE="$TEST_DIR/logs/5a-full_analysis-$(date +%Y%m%d-%H%M%S).log"
passed=0
failed=0

echo ""
echo "Running: win_full ($(date +%H:%M:%S))"

python3 scripts/run_test.py --run "win_full" -y --wait 2>&1 | tee -a "$LOG_FILE"

if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "✓ win_full PASSED"
    ((passed++))
else
    echo "✗ win_full FAILED"
    ((failed++))
fi

print_footer "5a" "$passed" "$failed" "$LOG_FILE"

[ "$failed" -eq 0 ]

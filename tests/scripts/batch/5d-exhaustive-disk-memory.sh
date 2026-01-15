#!/bin/bash
# 5d: Exhaustive - Disk + Memory (~240 min)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"
BATCH_NAME="5d-exhaustive-disk-memory"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"
tests=("win_disk_and_memory")
passed=0; failed=0
for test in "${tests[@]}"; do
    if python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"; then
        ((passed++))
    else
        ((failed++))
    fi
done
echo "BATCH 5d COMPLETE - Passed: $passed, Failed: $failed"

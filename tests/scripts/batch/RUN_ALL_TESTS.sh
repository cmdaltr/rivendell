#!/bin/bash
# Run all test batches sequentially with Docker restarts
# This master script runs all batches 1-4 in order
# WARNING: Batch 5 tests (extreme tests) not included - run manually if needed

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "" | tee -a "$LOG_FILE"
    echo "WARNING: Docker is not running" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # Offer to start Docker
    read -p "Would you like to start Docker now? [Y/n] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "" | tee -a "$LOG_FILE"
        echo "Please start Docker manually and try again:" | tee -a "$LOG_FILE"
        echo "  macOS:   Open Docker Desktop application" | tee -a "$LOG_FILE"
        echo "  Linux:   sudo systemctl start docker" | tee -a "$LOG_FILE"
        echo "  Windows: Start Docker Desktop" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # Start Docker based on platform
    echo "" | tee -a "$LOG_FILE"
    echo "Starting Docker..." | tee -a "$LOG_FILE"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open -a Docker
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Attempting to start Docker service..." | tee -a "$LOG_FILE"
        sudo systemctl start docker 2>&1 | tee -a "$LOG_FILE"
    else
        # Windows or unknown
        echo "Please start Docker Desktop manually" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # Wait for Docker to be ready
    echo "Waiting for Docker to start (max 60 seconds)..." | tee -a "$LOG_FILE"
    for i in {1..60}; do
        if docker ps &> /dev/null; then
            echo "✓ Docker is now running" | tee -a "$LOG_FILE"
            echo "" | tee -a "$LOG_FILE"
            break
        fi
        sleep 1
        if [ $i -eq 60 ]; then
            echo "" | tee -a "$LOG_FILE"
            echo "ERROR: Docker failed to start within 60 seconds" | tee -a "$LOG_FILE"
            echo "Please start Docker manually and try again" | tee -a "$LOG_FILE"
            echo "" | tee -a "$LOG_FILE"
            exit 1
        fi
    done
fi

echo "========================================"
echo "RUNNING ALL TEST BATCHES"
echo "========================================"
echo "Started: $(date)"
echo ""
echo "Group 1 - File Collection"
echo "Group 2 - Analysis"
echo "Group 3 - Detection"
echo "Group 4 - SIEM Exports"
echo "Group 5 - Comprehensive (LONG!)"
echo ""
echo "Estimated total duration: ~30+ hours"
echo ""
echo "Press Ctrl+C within 10s to abort..."
sleep 10

BATCHES=(
    "1a_archive.sh"
    "1b_collect--lnk-docs.sh"
    "1c_collect--bin-hidden-scripts.sh"
    "1d_collect--mail-virtual-web.sh"
    "2a-profiles-vss.sh"
    "2b-memory.sh"
    "2c-brisk.sh"
    "2d-collect-all.sh"
    "3a-ioc-extraction.sh"
    "3b-keywords.sh"
    "3c-yara.sh"
    "3d-yara-memory.sh"
    "4a-splunk-export.sh"
    "4b-elastic-export.sh"
    "4c-navigator-export.sh"
    "4d-siem-nav-export.sh"
    "5a-full_analysis.sh"
    "5b-exhaustive-disk.sh"
    "5c-exhaustive-memory.sh"
    "5d-exhaustive-disk-memory.sh"
)

total_batches=${#BATCHES[@]}
current_batch=0
passed_batches=0
failed_batches=0

for batch in "${BATCHES[@]}"; do
    ((current_batch++))
    echo ""
    echo "========================================"
    echo "BATCH $current_batch/$total_batches: $batch"
    echo "Time: $(date +%H:%M:%S)"
    echo "========================================"

    if bash "$batch"; then
        echo "✓ Batch $batch PASSED"
        ((passed_batches++))
    else
        echo "✗ Batch $batch FAILED"
        ((failed_batches++))
    fi

    # Restart Docker between batches for extra safety
    if [ $current_batch -lt $total_batches ]; then
        echo ""
        echo "Restarting Docker between batches..."
        docker restart rivendell-backend rivendell-celery-worker
        echo "Waiting 30s..."
        sleep 30
    fi
done

echo ""
echo "========================================"
echo "ALL BATCHES COMPLETE"
echo "========================================"
echo "Passed batches: $passed_batches"
echo "Failed batches: $failed_batches"
echo "Ended: $(date)"
echo ""
echo "Test outputs are in:"
echo "  /Volumes/Media5TB/rivendell_imgs/tests/"
echo "  (or your configured TEST_OUTPUT_PATH)"

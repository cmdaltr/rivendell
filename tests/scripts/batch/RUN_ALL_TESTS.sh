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
echo "RUNNING ALL TEST BATCHES (1-4)"
echo "========================================"
echo "Started: $(date)"
echo ""
echo "This will run batches 1a through 4c sequentially"
echo "Estimated total duration: ~9-10 hours"
echo ""
echo "Batch 5 (extreme tests) are NOT included"
echo "Run those manually if needed"
echo ""
echo "Press Ctrl+C within 10s to abort..."
sleep 10

BATCHES=(
    "batch1a-archive-lnk.sh"
    "batch1b-archive-docs.sh"
    "batch1c-bin-hidden.sh"
    "batch2a-mail-scripts.sh"
    "batch2b-virtual-web.sh"
    "batch2c-extraction.sh"
    "batch3a-profiles-vss.sh"
    "batch3b-yara-memory.sh"
    "batch4a-brisk.sh"
    "batch4b-keywords.sh"
    "batch4c-collect-all.sh"
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

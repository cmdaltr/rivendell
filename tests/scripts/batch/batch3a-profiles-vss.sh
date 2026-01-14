#!/bin/bash
# Batch 3a: User Profiles + VSS (~60 min)
# User profile and shadow copy tests

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$TEST_DIR"

BATCH_NAME="batch3a-profiles-vss"
LOG_FILE="$TEST_DIR/logs/${BATCH_NAME}-$(date +%Y%m%d-%H%M%S).log"

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

# Restart Docker at beginning of batch for clean state
echo "Restarting Docker containers for clean state..." | tee -a "$LOG_FILE"
docker restart rivendell-backend rivendell-celery-worker 2>&1 | tee -a "$LOG_FILE"
echo "Waiting 30s for services to restart..." | tee -a "$LOG_FILE"
sleep 30

echo "Verifying backend..." | tee -a "$LOG_FILE"
python3 scripts/run_test.py --status 2>&1 | tee -a "$LOG_FILE" || echo "⚠ Backend may need more time" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"




echo "======================================"
echo "BATCH 3a: User Profiles + VSS"
echo "======================================"
echo "Start: $(date)"
echo "Log: $LOG_FILE"
echo "Estimated duration: ~60 minutes"
echo ""

# Test list (2 tests)
tests=(
    "win_userprofiles"
    "win_vss"
)

passed=0
failed=0

test_count=${#tests[@]}
current=0

for test in "${tests[@]}"; do
    ((current++))
    echo ""
    echo "========================================"
    echo "Running: $test ($current/$test_count) ($(date +%H:%M:%S))"
    echo "========================================"

    if python3 scripts/run_test.py --run "$test" -y --wait 2>&1 | tee -a "$LOG_FILE"; then
        echo "✓ $test PASSED"
        ((passed++))
    else
        echo "✗ $test FAILED"
        ((failed++))
    fi

    # Restart Docker between tests to free resources (prevents crashes)
    if [ $current -lt $test_count ]; then
        echo ""
        echo "Restarting Docker to free resources..."
        docker restart rivendell-backend rivendell-celery-worker 2>&1 | tee -a "$LOG_FILE"
        echo "Waiting 30s for services to restart..."
        sleep 30

        # Verify backend is back up
        echo "Verifying backend..."
        python3 scripts/run_test.py --status 2>&1 | tee -a "$LOG_FILE" || echo "⚠ Backend may need more time"
        echo ""
    fi
done

echo ""
echo "======================================"
echo "BATCH 3a COMPLETE"
echo "======================================"
echo "Passed: $passed"
echo "Failed: $failed"
echo "End: $(date)"
echo "Log: $LOG_FILE"

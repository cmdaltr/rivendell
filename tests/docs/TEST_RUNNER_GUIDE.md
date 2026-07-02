# Rivendell Test Runner Guide

This guide explains how to run Rivendell tests safely and efficiently, preventing Docker crashes through automatic container restarts.

## Quick Start

### Run a Single Test (Recommended)
```bash
cd tests
./run_single_test.sh <test_name>

# Examples:
./run_single_test.sh win_archive
./run_single_test.sh win_memory_basic
```

### Run a Test Batch
```bash
cd tests/scripts/batch
./batch1a-archive-lnk.sh          # Quick tests (~65 min)
./batch2a-mail-scripts.sh         # Medium tests (~60 min)
```

### Run All Tests (9-10 hours)
```bash
cd tests/scripts/batch
./RUN_ALL_TESTS.sh
```

---

## Available Scripts

### 1. Single Test Runner (`run_single_test.sh`)

Runs one test with automatic Docker restart afterward to prevent resource exhaustion.

**Usage:**
```bash
./run_single_test.sh <test_name> [--no-restart]
```

**Options:**
- `<test_name>` - Name of the test to run (required)
- `--no-restart` - Skip Docker restart (optional)

**Examples:**
```bash
# Run test with automatic restart (recommended)
./run_single_test.sh win_archive

# Run test without restart (not recommended for long-running tests)
./run_single_test.sh win_brisk --no-restart

# List available tests
./run_single_test.sh
```

**Features:**
- ✅ Checks Docker status before starting
- ✅ Restarts Docker containers after test completes
- ✅ Verifies backend is responsive after restart
- ✅ Creates timestamped logs in `tests/logs/`
- ✅ Returns proper exit codes for CI/CD integration

---

### 2. Batch Test Scripts (`batch*.sh`)

Run multiple related tests sequentially with automatic Docker restarts between tests.

**Batch Overview:**

| Batch | Tests | Duration | Description |
|-------|-------|----------|-------------|
| **1a** | 2 | ~65 min | Archive + LNK file collection |
| **1b** | 2 | ~60 min | Archive + Document collection |
| **1c** | 2 | ~75 min | Binary + Hidden file collection |
| **2a** | 2 | ~60 min | Mail + Script extraction |
| **2b** | 2 | ~60 min | Virtual machines + Web artifacts |
| **2c** | 2 | ~60 min | Advanced extraction features |
| **3a** | 2 | ~60 min | User profiles + VSS |
| **3b** | 3 | ~90 min | YARA + Memory analysis |
| **4a** | 1 | ~10 min | Brisk analysis mode |
| **4b** | 1 | ~90 min | Keyword search |
| **4c** | 1 | ~90 min | Collect all files |
| **5a** | 1 | 2-4+ hrs | Full disk analysis |
| **5b** | 1 | 2-4+ hrs | Disk + Memory combined |
| **5c** | 1 | 2-4+ hrs | SIEM exports (Splunk/Elastic/Navigator) |
| **5d** | 1 | 2-4+ hrs | Memory + SIEM combined |

**Usage:**
```bash
cd tests/scripts/batch
./batch1a-archive-lnk.sh
```

**Features:**
- ✅ Automatically restarts Docker **between each test**
- ✅ Waits 30s for services to stabilize after restart
- ✅ Verifies backend responsiveness before continuing
- ✅ Creates timestamped logs in `tests/logs/`
- ✅ Displays pass/fail summary at end

---

### 3. Master Script (`RUN_ALL_TESTS.sh`)

Runs all batches 1a through 4c sequentially (excludes extreme batch 5 tests).

**Usage:**
```bash
cd tests/scripts/batch
./RUN_ALL_TESTS.sh
```

**Features:**
- ✅ Runs batches 1a-4c (11 batches, ~9-10 hours total)
- ✅ Restarts Docker between each batch
- ✅ Displays overall pass/fail summary
- ⚠️ Does NOT include batch 5 (extreme tests) - run those manually if needed

**Example Output:**
```
BATCH 1/11: batch1a-archive-lnk.sh
✓ Batch batch1a-archive-lnk.sh PASSED
Restarting Docker between batches...

BATCH 2/11: batch1b-archive-docs.sh
...
```

---

## Why Automatic Restarts?

**Problem:** Rivendell forensic analysis is resource-intensive. Running multiple tests consecutively can cause Docker to crash due to memory exhaustion, even though individual tests complete successfully.

**Solution:** Restart Docker containers between tests to free accumulated resources (memory, file handles, cache).

**Benefits:**
- Prevents Docker crashes during long test runs
- Each test starts with a clean environment
- Tests complete successfully even if Docker crashes afterward
- Output files are preserved on the external drive

---

## Docker Resource Requirements

### Recommended Settings

Open **Docker Desktop → Settings → Resources**:

- **Memory**: 12-16GB (minimum 8GB)
- **CPUs**: 6-8 cores
- **Disk**: 100GB+ free space
- **Swap**: 2GB+

### Current Limits (docker-compose.yml)

- **Celery Worker**: 8GB max, 2GB reserved
- **Elasticsearch**: 2GB max, 1GB reserved
- **Splunk**: 4GB max, 1GB reserved

---

## Test Output Locations

### Platform-Specific Paths

**macOS:**
```
/Volumes/[ExternalDrive]/rivendell_imgs/tests/
```

**Linux:**
```
/mnt/[mount]/rivendell_imgs/tests/
/media/[user]/[drive]/rivendell_imgs/tests/
```

**Windows:**
```
[D-Z]:/rivendell_imgs/tests/
```

### Output Structure

```
tests/
├── win_archive/
│   └── win7-64-nfury-c-drive.E01/
│       ├── artefacts/
│       │   ├── raw/        # Raw collected files
│       │   └── cooked/     # Parsed artifacts (JSON/CSV)
│       └── audit_log.csv
├── win_collect_files_lnk/
│   └── ...
└── win_memory_basic/
    └── ...
```

### Override Default Paths

```bash
export TEST_IMAGES_PATH="/custom/path/to/images"
export TEST_OUTPUT_PATH="/custom/path/to/output"
./run_single_test.sh win_archive
```

---

## Logs

All test runs create timestamped logs in `tests/logs/`:

```bash
# Single test logs
tests/logs/single-win_archive-20260112-152344.log

# Batch logs
tests/logs/batch1a-archive-lnk-20260112-152344.log
```

**View recent logs:**
```bash
ls -lt tests/logs/*.log | head -5
tail -50 tests/logs/batch1a-*.log
```

---

## Job Management

### Check Job Status

Use the `status.sh` script to monitor running jobs:

**Basic status:**
```bash
./scripts/status.sh
```

**Show full job IDs:**
```bash
./scripts/status.sh --full
# or
./scripts/status.sh -f
```

**Watch mode (auto-refresh every 5 seconds):**
```bash
./scripts/status.sh --watch
# or
./scripts/status.sh -w
```

**Watch with full IDs:**
```bash
./scripts/status.sh --full --watch
```

Example output:
```
======================================================================
  JOB STATUS SUMMARY
======================================================================
  Running: 1  |  Pending: 0  |  Completed: 0  |  Failed: 0
======================================================================

  RUNNING:
    🔄 TEST_win_brisk (45%)
       ID: d48fc76f-18b4-4bb8-9579-8c742a976349
```

### Stop Running Jobs

Use the `stop-jobs.sh` script to cancel jobs:

**Cancel ALL running/pending jobs:**
```bash
./scripts/stop-jobs.sh
```

**Cancel specific job by ID:**
```bash
# First, get the job ID
./scripts/status.sh --full

# Then stop that specific job
./scripts/stop-jobs.sh d48fc76f-18b4-4bb8-9579-8c742a976349
```

**Skip confirmation prompt:**
```bash
./scripts/stop-jobs.sh -y                                    # All jobs
./scripts/stop-jobs.sh d48fc76f-18b4-4bb8-9579-8c742a976349 -y  # Specific job
```

---

## Troubleshooting

### Docker Not Running

**All scripts now offer to start Docker automatically!**

```bash
$ ./batch1a-archive-lnk.sh

WARNING: Docker is not running
Would you like to start Docker now? [Y/n] y

Starting Docker...
Waiting for Docker to start (max 60 seconds)...
✓ Docker is now running
```

**Or start manually if you prefer:**
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker

# Windows
# Start Docker Desktop from Start Menu
```

### Backend Not Responding
```bash
# Check backend status
python3 tests/run_test.py --status

# Restart containers
docker restart rivendell-backend rivendell-celery-worker

# Wait for startup
sleep 30
python3 tests/run_test.py --status
```

### Out of Disk Space
```bash
# Check available space
df -h /Volumes/*/rivendell_imgs  # macOS
df -h /mnt/*/rivendell_imgs      # Linux

# Clean old test outputs
rm -rf /Volumes/*/rivendell_imgs/tests/win_*
```

### Docker Crashes During Tests
This is normal for long-running tests! The automatic restart scripts handle this.

**If crashes happen too frequently:**
1. Increase Docker memory allocation (Settings → Resources)
2. Run one test at a time with `run_single_test.sh`
3. Restart Docker manually between tests

---

## Best Practices

### For Quick Testing
```bash
# Run a single fast test to verify system works
./run_single_test.sh win_brisk
```

### For Overnight Runs
```bash
# Start batch in evening, check results in morning
nohup ./batch1a-archive-lnk.sh > /tmp/batch1a.log 2>&1 &

# Or run the master script
nohup ./RUN_ALL_TESTS.sh > /tmp/all_tests.log 2>&1 &
```

### For CI/CD Integration
```bash
# Single tests return proper exit codes
if ./run_single_test.sh win_archive; then
    echo "Test passed"
else
    echo "Test failed"
    exit 1
fi
```

---

## FAQ

**Q: Do I need to restart Docker manually?**
A: No, all scripts now handle restarts automatically.

**Q: Can I run multiple tests in parallel?**
A: No, tests must run sequentially due to shared Docker resources.

**Q: What if Docker crashes during a test?**
A: The test outputs are written to the external drive and are preserved. Just restart Docker and check the output directory.

**Q: How do I know if a test completed successfully?**
A: Check the log file for "✓ PASSED" or look for output in `/Volumes/*/rivendell_imgs/tests/[test_name]/`

**Q: Should I run batch 5 (extreme tests)?**
A: Only if you have 2-4+ hours per test and need memory analysis or SIEM exports. Consider running those individually overnight.

---

## Summary Commands

```bash
# List available tests
cd tests && python3 run_test.py --list

# Run one test (recommended for testing)
./run_single_test.sh win_archive

# Run a quick batch
cd scripts/batch && ./batch1a-archive-lnk.sh

# Run all tests (9-10 hours)
cd scripts/batch && ./RUN_ALL_TESTS.sh

# Check results
ls -lh /Volumes/Media5TB/rivendell_imgs/tests/

# View logs
ls -lt logs/*.log | head -5
```

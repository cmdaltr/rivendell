# File Descriptor Management

## Problem

When processing large forensic images, Rivendell can hit the operating system's file descriptor limit, causing this error:

```
OSError: [Errno 24] Too many open files: '/path/to/file'
```

This happens when:
- Processing many small files simultaneously
- Collecting files from large disk images
- Running multiple tests back-to-back without cleanup

## Solution

We've implemented **automatic retry logic** that gracefully handles file descriptor exhaustion:

1. **Catches the error** instead of failing immediately
2. **Triggers garbage collection** to close unreferenced file handles
3. **Waits with exponential backoff** to allow system cleanup
4. **Retries the operation** up to 5 times
5. **Only fails** if all retries are exhausted

## Usage

### Option 1: Decorator (Recommended for Functions)

Wrap any function that opens many files:

```python
from analysis.utils import retry_on_fd_limit

@retry_on_fd_limit(max_retries=5, initial_wait=0.5)
def process_collected_files(file_paths):
    """Process a large collection of files."""
    results = []
    for path in file_paths:
        with open(path, 'rb') as f:
            data = f.read()
            results.append(analyze(data))
    return results

# Function will automatically retry if it hits file descriptor limits
results = process_collected_files(many_files)
```

### Option 2: Safe Open (Drop-in Replacement)

Replace `open()` with `safe_open()`:

```python
from analysis.utils import safe_open

# Before:
with open('/path/to/file', 'r') as f:
    data = f.read()

# After:
with safe_open('/path/to/file', 'r') as f:
    data = f.read()
```

### Option 3: Monitor File Descriptor Usage

Check usage and get warnings:

```python
from analysis.utils import check_fd_usage, get_fd_limit

# Check current usage
stats = check_fd_usage(warn_threshold=0.8)
print(f"FD usage: {stats['used']}/{stats['soft_limit']} ({stats['percent']}%)")

# Get limits
soft, hard = get_fd_limit()
print(f"Limits: {soft} (soft), {hard} (hard)")
```

## Configuration

### Decorator Options

```python
@retry_on_fd_limit(
    max_retries=5,          # Number of retry attempts
    initial_wait=0.5,       # Initial wait time (seconds)
    backoff_multiplier=2.0, # Exponential backoff multiplier
    max_wait=10.0,          # Maximum wait between retries
    trigger_gc=True         # Trigger garbage collection on retry
)
def my_function():
    pass
```

### Example: Aggressive Retry for Critical Operations

```python
@retry_on_fd_limit(
    max_retries=10,         # More retries
    initial_wait=1.0,       # Longer initial wait
    max_wait=30.0,          # Allow longer waits
    trigger_gc=True
)
def critical_file_operation():
    """This operation must succeed."""
    pass
```

### Example: Quick Fail for Non-Critical Operations

```python
@retry_on_fd_limit(
    max_retries=2,          # Fewer retries
    initial_wait=0.2,       # Quick retry
    max_wait=1.0            # Fail fast
)
def optional_file_operation():
    """Can fail without major impact."""
    pass
```

## Integration Points

### File Collection (High Priority)

```python
# In file collection code
from analysis.utils import retry_on_fd_limit

@retry_on_fd_limit(max_retries=10)
def collect_files_from_image(mount_point, output_dir, filters):
    """Collect files matching filters from mounted image."""
    collected = []
    for root, dirs, files in os.walk(mount_point):
        for filename in files:
            if matches_filter(filename, filters):
                src = os.path.join(root, filename)
                dst = os.path.join(output_dir, filename)
                with safe_open(src, 'rb') as fin:
                    with safe_open(dst, 'wb') as fout:
                        shutil.copyfileobj(fin, fout)
                collected.append(dst)
    return collected
```

### IOC Extraction

```python
@retry_on_fd_limit(max_retries=5)
def extract_iocs_from_files(file_list):
    """Extract IOCs from collected files."""
    iocs = []
    for filepath in file_list:
        with safe_open(filepath, 'r', errors='ignore') as f:
            content = f.read()
            iocs.extend(find_iocs(content))
    return iocs
```

### Timeline Generation

```python
@retry_on_fd_limit(max_retries=5)
def generate_timeline(events_dir):
    """Generate timeline from event files."""
    events = []
    for filename in os.listdir(events_dir):
        filepath = os.path.join(events_dir, filename)
        with safe_open(filepath, 'r') as f:
            events.extend(json.load(f))
    return sorted(events, key=lambda x: x['timestamp'])
```

## Benefits

### Before (Hard Failure)

```
Processing files...
OSError: [Errno 24] Too many open files
❌ Test FAILED
```

### After (Automatic Recovery)

```
Processing files...
⚠️  File descriptor limit reached (attempt 1/5): Too many open files.
    Waiting 0.5s and retrying...
✓ Garbage collection freed 127 objects
✓ Retry successful
✓ Test PASSED
```

## Monitoring

Add logging to track file descriptor usage:

```python
import logging
from analysis.utils import check_fd_usage

logger = logging.getLogger(__name__)

def before_processing():
    stats = check_fd_usage(warn_threshold=0.7)
    logger.info(
        f"Starting processing - FD usage: {stats['used']}/{stats['soft_limit']} "
        f"({stats['percent']}%)"
    )

def after_processing():
    stats = check_fd_usage()
    logger.info(
        f"Finished processing - FD usage: {stats['used']}/{stats['soft_limit']} "
        f"({stats['percent']}%)"
    )
```

## Docker Configuration

We've already increased Docker container limits:

```yaml
services:
  celery-worker:
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

Combined with the retry logic, this provides:
1. **High limits** (65,536) to prevent most errors
2. **Automatic retry** if limits are still hit
3. **Graceful degradation** instead of hard failures

## Testing

Test the retry logic:

```bash
# Run the utility test
python3 /Users/ben/Library/CloudStorage/OneDrive-Personal/Projects/GitHub/rivendell/src/analysis/utils/file_limits.py
```

Output:
```
File Descriptor Limit Management Utility
==================================================
Current FD limits: 65536 (soft), 65536 (hard)
Currently open FDs: 42
Function executed successfully
Test result: success

FD Usage Statistics:
  used: 42
  soft_limit: 65536
  hard_limit: 65536
  percent: 0.1
  available: 65494
```

## Troubleshooting

### Logs show repeated retries

If you see many retries in logs, consider:
1. Increasing `max_retries` for that operation
2. Increasing `initial_wait` to give more time for cleanup
3. Adding explicit file closing in loops
4. Processing files in smaller batches

### Still hitting limits after all retries

If `FileDescriptorLimitError` is raised:
1. Check if system limit needs increasing: `ulimit -n`
2. Verify Docker container limits: `docker exec rivendell-celery-worker sh -c "ulimit -n"`
3. Add batch processing to handle files in chunks
4. Profile code to find file handle leaks

## Best Practices

1. **Always close files explicitly** - Don't rely on garbage collection
2. **Use context managers** - `with open()` ensures cleanup
3. **Process in batches** - Don't open 10,000 files at once
4. **Monitor usage** - Log FD usage at operation boundaries
5. **Use safe_open** - For code that must be bulletproof

## Summary

- ✅ **Increased Docker limits** to 65,536 (was 256)
- ✅ **Added retry logic** with automatic recovery
- ✅ **Created utilities** for easy integration
- ✅ **Added delays** between batch tests (30s default)

This three-layer approach ensures reliable operation:
1. **Prevention** (high limits)
2. **Recovery** (automatic retry)
3. **Isolation** (delays between tests)

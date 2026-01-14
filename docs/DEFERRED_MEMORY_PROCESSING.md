# Deferred Memory Processing Workflow

## Overview

Rivendell/Elrond implements a **deferred memory processing** architecture that separates disk image collection from memory image processing. This ensures proper phase separation and prevents processing conflicts when both disk and memory images are provided together.

## Key Concept

**Memory images are "parked" during the Collection Phase and processed after disk image collection completes.**

This is critical because:
- Disk and memory images require different processing pipelines
- Memory images should not interfere with disk artifact collection
- Volatility processing for memory images can be resource-intensive
- Phase separation provides clearer progress tracking and error handling

## Image Format

Images are identified using a three-part format:

```
filename::mount_point::type
```

**Examples:**
- `win7-64-disk.E01::/mnt/elrond_mount00::disk`
- Linux: `win7-64-nfury-memory-raw.001::/mnt/external/rivendell_imgs/::memory`
- macOS: `win7-64-nfury-memory-raw.001::/Volumes/ExternalDrive/rivendell_imgs/::memory`
- Windows: `win7-64-nfury-memory-raw.001::D:/rivendell_imgs/::memory`

**Field Breakdown:**
- **[0] filename**: The base image filename
- **[1] mount_point**: Where the image is mounted (for disk) or source directory (for memory)
- **[2] type**: Either `disk` or `memory`

## Processing Phases

### Phase 1: Identification (in elrond.py)

When images are first identified:

1. **Disk images**: Added to `imgs` dict for immediate processing
2. **Memory images**:
   - Profile identified via `identify_memory_image()`
   - Profile saved to `.memory_profiles.json` via `save_memory_profile()`
   - **NOT added to `imgs` dict** - they are "parked"

**Location**: `src/analysis/rivendell/core/identify.py:186`

```python
# The actual memory processing (artefact extraction) is deferred to the
# processing phase via process_deferred_memory().
```

### Phase 2: Collection (collect.py)

**Only disk images are processed during collection.**

Memory images should be filtered out using image type detection:

```python
# CORRECT way to check image type:
img_type = img.split("::")[2] if len(img.split("::")) > 2 else ""
if img_type != "memory":
    # Process disk artifacts
```

**Location**: `src/analysis/rivendell/collect/collect.py:161-405`

### Phase 3: Processing (select.py)

**Only disk artifacts are processed during the main processing phase.**

Memory images must be excluded from artifact processing:

```python
# CORRECT way to filter out memory images:
img_type = img.split("::")[2] if len(img.split("::")) > 2 else ""
if img_basename not in str(processed_imgs) and img_type != "memory":
    # Process disk artifacts
```

**Location**: `src/analysis/rivendell/process/select.py:113-117`

### Phase 3b: Deferred Memory Processing (elrond.py)

**After all disk images are processed**, memory images are loaded from the saved profiles:

```python
# Load saved memory profiles
has_deferred_memory = bool(load_memory_profiles(output_directory))
if volatility or has_deferred_memory:
    process_deferred_memory(
        verbosity,
        output_directory,
        flags,
        mount_point,
    )
```

**Location**: `src/analysis/elrond.py:730-737`

**Implementation**: `src/analysis/rivendell/core/identify.py:275-359`

The `process_deferred_memory()` function:
1. Loads profiles from `.memory_profiles.json`
2. For each saved memory image:
   - Reconstructs the image info
   - Calls `process_memory()` with Volatility 3
   - Extracts memory artifacts to output directory

### Phase 4: Analysis

All images (disk and memory) are analyzed for IOCs, keywords, YARA rules, etc.

## Memory Profile Storage

Profiles are saved to: `{output_directory}/.memory_profiles.json`

**Example profile (macOS):**
```json
{
  "win7-64-nfury-memory-raw.001": {
    "profile": "Windows",
    "platform": "Windows memory",
    "volchoice": "3",
    "path": "/Volumes/ExternalDrive/rivendell_imgs/win7-64-nfury-memory-raw.001",
    "mount_point": "/Volumes/ExternalDrive/rivendell_imgs/",
    "vss": false,
    "vssmem": "",
    "memtimeline": ""
  }
}
```

**Platform-specific path examples:**
- Linux: `/mnt/external/rivendell_imgs/` or `/media/user/drive/rivendell_imgs/`
- macOS: `/Volumes/ExternalDrive/rivendell_imgs/`
- Windows: `D:/rivendell_imgs/` or `E:/rivendell_imgs/`

## Critical Bug: Image Type Detection

### The Bug

**Three locations were checking the WRONG index** when determining image type:

```python
# WRONG - checks mount_point (index 1):
if img.split("::")[1].endswith("memory"):
    # ...

# CORRECT - checks type (index 2):
img_type = img.split("::")[2] if len(img.split("::")) > 2 else ""
if img_type == "memory":
    # ...
```

### Why This Caused Issues

When processing `win7-64-disk.E01::/mnt/elrond_mount00::disk`:
- **Wrong check**: `img.split("::")[1]` = "/mnt/elrond_mount00" (doesn't end with "memory" ✓)
- **Correct check**: `img.split("::")[2]` = "disk" (not "memory" ✓)

But with output directory named `win_disk_and_memory/`:
- Artifacts had paths like: `/tests/win_disk_and_memory/artefacts/file.ext`
- String contains "memory" = False positive when using path-based detection

### Affected Files (FIXED)

1. **select.py:113-117** - Processing phase artifact filtering
2. **collect.py:183-184** - Collection phase memory detection
3. **core.py:232-234** - Timeline phase memory filtering

### The Fix

All three locations now use:

```python
img_type = img.split("::")[2] if len(img.split("::")) > 2 else ""
if img_type != "memory":
    # Process disk-specific logic
```

## File Locations

| File | Purpose | Key Functions/Lines |
|------|---------|-------------------|
| `src/analysis/elrond.py` | Main orchestration | Lines 730-737: Deferred memory processing |
| `src/analysis/rivendell/core/identify.py` | Memory identification & deferred processing | Lines 17-42: save/load profiles<br>Lines 186: Deferral comment<br>Lines 275-359: process_deferred_memory() |
| `src/analysis/rivendell/core/core.py` | Phase orchestration | Lines 54-121: Phase control logic |
| `src/analysis/rivendell/collect/collect.py` | Artifact collection | Lines 161-405: Collection loop<br>Lines 183-184: Memory filtering |
| `src/analysis/rivendell/process/select.py` | Artifact processing | Lines 113-117: Memory filtering |
| `src/analysis/rivendell/memory/memory.py` | Memory processing | Lines 131-322: process_memory() |

## Workflow Diagram

```
┌─────────────────────────────────────────────────┐
│ Phase 1: Identification                         │
├─────────────────────────────────────────────────┤
│ ┌─────────────┐          ┌──────────────┐      │
│ │ Disk Image  │──────────>│ Add to imgs  │      │
│ └─────────────┘          └──────────────┘      │
│                                                  │
│ ┌──────────────┐         ┌────────────────────┐│
│ │ Memory Image │────────>│ Save to            ││
│ └──────────────┘         │ .memory_profiles   ││
│                          │ (PARKED)           ││
│                          └────────────────────┘│
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Phase 2: Collection                             │
├─────────────────────────────────────────────────┤
│ Process ONLY disk images from imgs dict         │
│ - Filter: img_type != "memory"                  │
│ - Collect system artifacts                      │
│ - Extract files                                 │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Phase 3: Processing                             │
├─────────────────────────────────────────────────┤
│ Process ONLY disk artifacts                     │
│ - Filter: img_type != "memory"                  │
│ - Parse registry, logs, browsers, etc.          │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Phase 3b: Deferred Memory Processing            │
├─────────────────────────────────────────────────┤
│ Load .memory_profiles.json                      │
│ For each memory image:                          │
│   - Reconstruct image info                      │
│   - Run Volatility 3 plugins                    │
│   - Extract memory artifacts                    │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Phase 4: Analysis                               │
├─────────────────────────────────────────────────┤
│ Analyze ALL artifacts (disk + memory)           │
│ - IOC extraction                                │
│ - Keyword searching                             │
│ - YARA scanning                                 │
│ - Timeline generation                           │
└─────────────────────────────────────────────────┘
```

## Testing

### Test Case: `test_win_disk_and_memory`

**Purpose**: Verify that disk and memory images can be processed together without conflicts.

**Expected Behavior**:
1. Disk image is collected and processed during Collection/Processing phases
2. Memory image is identified and parked (saved to `.memory_profiles.json`)
3. After disk processing completes, memory image is processed via `process_deferred_memory()`
4. Both sets of artifacts are analyzed in Analysis phase

**Location**: `tests/test_rivendell_workflow.py::test_win_disk_and_memory`

**Test Images**:
- Disk: `win7-64-disk.E01` (Windows 7 x64 disk image)
- Memory: `win7-64-nfury-memory-raw.001` (Windows 7 x64 memory dump)

### Known Issues - RESOLVED

**RecursionError at 38% Processing Phase - FIXED (2026-01-05)**:
- Test was failing with `RecursionError: maximum recursion depth exceeded`
- Occurred during Processing Phase at 38% progress when processing `hiberfil.sys`
- **RESOLUTION**: Increased Python recursion limit from 1000 to 5000 during Processing Phase

**ROOT CAUSE IDENTIFIED (2026-01-05)**:

The recursion is caused by `hiberfil.sys` processing during the disk Processing Phase.

**Call Stack:**
1. `select_pre_process_artefacts()` identifies `hiberfil.sys` from disk image
2. Calls `determine_vss_image()` → `process_artefacts()`
3. `process_artefacts()` line 344 checks: `elif artefact.endswith("hiberfil.sys") and volatility:`
4. Calls `process_hiberfil()` at line 352
5. **`process_hiberfil()` calls `process_memory()` directly** (windows.py:705)
6. `process_memory()` runs full Volatility processing (`assess_volatility_choice()` → `extract_memory_artefacts()`)
7. Volatility's internal processing or deep artifact extraction causes RecursionError

**The Architectural Problem:**

`hiberfil.sys` (hibernation file) found on disk images is being processed **synchronously during the disk Processing Phase** using the full memory processing pipeline. This violates the deferred memory processing architecture and causes deep recursion through Volatility's plugin system.

**Location of Bug:**
- `src/analysis/rivendell/process/process.py:344-365` - Triggers `hiberfil.sys` processing
- `src/analysis/rivendell/process/windows.py:684-717` - Calls `process_memory()` directly

**Why This Causes Recursion:**
1. Volatility 3's plugin system has deep internal call stacks
2. Processing hibernation files extracts many artifacts, each triggering nested processing
3. Python's default recursion limit (~1000) is exceeded
4. Unlike standalone memory images (which are deferred), `hiberfil.sys` embedded in disk images is processed immediately

**IMPLEMENTED FIX (2026-01-05):**

Increased Python recursion limit during the Processing Phase to handle Volatility's deep call stacks.

**Implementation:**
- File: `src/analysis/rivendell/process/select.py`
- Added `sys.setrecursionlimit(5000)` at start of `select_pre_process_artefacts()`
- Wrapped in try/finally block to ensure limit is restored after processing
- Recursion limit is increased from default 1000 to 5000

**Code Changes:**
```python
def select_pre_process_artefacts(...):
    stage = "processing"
    process_list, artefacts_list = [], []

    # Increase recursion limit for Volatility processing of memory artifacts (hiberfil.sys, etc.)
    # Volatility 3's plugin system has deep call stacks that exceed Python's default limit (1000)
    original_recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(5000)

    try:
        # ... all processing logic ...
    finally:
        # Restore original recursion limit (always executed, even if exception occurs)
        sys.setrecursionlimit(original_recursion_limit)
```

**Why This is the Correct Fix:**

The initial investigation suggested deferring `hiberfil.sys` processing (like standalone memory images), but this was **architecturally incorrect**:

- **Standalone memory images** (`.raw`, `.mem`): Should be deferred to Phase 3b
- **`hiberfil.sys`** (disk artifact): Should be collected and processed during disk phases

The recursion issue is not architectural - it's simply that Volatility's deep processing exceeds Python's default recursion limit. Increasing the limit allows normal processing to complete.

**Alternative Solutions Considered:**

**Option 1: Defer `hiberfil.sys` Processing** (rejected - architecturally incorrect)
- Would violate the principle that disk artifacts are processed during disk processing
- `hiberfil.sys` is a disk artifact, not a standalone memory image

**Option 2: Skip `hiberfil.sys` Processing** (rejected - loses forensic value)
- Would lose valuable forensic data from hibernation files
- Not acceptable for a forensic tool

**Option 3: Process in subprocess** (may implement later if needed)
- Could isolate recursion issues to subprocess
- More complex, unnecessary if limit increase works

## Future Claude Code Context

When working on this codebase in the future, remember:

1. **Image format is critical**: Always check index [2] for image type, not [1]
2. **Memory images are deferred**: Never process memory images during Collection/Processing phases
3. **Profile storage**: `.memory_profiles.json` is the source of truth for deferred memory
4. **Phase separation**: Respect the phase boundaries - don't mix disk and memory processing
5. **Docker deployment**: Code is COPIED into container during build at `/opt/elrond-src/`, not mounted
6. **Test failures**: If tests fail at Processing Phase, check for recursion in artifact processing loops

## References

- Main orchestration: `src/analysis/elrond.py`
- Deferred processing implementation: `src/analysis/rivendell/core/identify.py`
- Phase control: `src/analysis/rivendell/core/core.py`
- Memory processing: `src/analysis/rivendell/memory/memory.py`
- Volatility integration: `src/analysis/rivendell/memory/plugins.py`

---

**Last Updated**: 2026-01-05
**Contributors**: Investigation by Claude Code (Sonnet 4.5)

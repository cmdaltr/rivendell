# Latest Changes - Rivendell v2.1.1

## Date: 2025-11-21

### Major Changes

#### 1. Enforced Installation of Core Dependencies
- **apfs-fuse**: Now automatically installed during Docker image build
  - Supports macOS APFS filesystem analysis
  - No runtime prompts or checks
  - Located at `/usr/local/bin/apfs-fuse`

- **Volatility3**: Now automatically installed and enforced
  - Latest memory forensics framework
  - Replaces optional Volatility 2.6
  - Windows symbol tables included
  - Accessible via `vol3` command

#### 2. Non-Interactive Mode for Web Interface
- Added `ELROND_NONINTERACTIVE` environment variable
- Created `safe_input()` utility function
- All user prompts automatically answered with defaults
- Prevents web interface jobs from hanging

#### 3. Mount Point Directory Handling
- Added existence checks for `/mnt/shadow_mount/` and `/mnt/vss/`
- Automatic directory creation when needed
- Prevents `FileNotFoundError` on macOS and other systems

#### 4. Path Validation Improvements
- Fixed file path vs directory path handling
- Automatically extracts directory from full file paths
- E01 files can now be passed directly instead of their parent directory

#### 5. UI/UX Improvements

**Error Message Positioning**:
- Navigator validation error now appears above "Review Your Selections"
- Better visibility before starting analysis
- Auto-clears when user fixes the issue

**Options Display**:
- Removed internal options from Enabled Options display
- Proper formatting: "VSS" (all caps), "User Profiles" (with space)
- Cleaner job details page

**Job Logs**:
- Removed ASCII art from web interface logs
- Removed Tolkien quotes from web interface logs
- Cleaner, more professional output
- ASCII art and quotes still available via CLI with `-l` flag

### Files Modified

#### Dockerfile
- Added cmake and FUSE dependencies
- Added apfs-fuse build from source
- Added Volatility3 installation with symbol tables
- Created symlink `/usr/local/bin/vol3` for easy access

#### Backend (Python)
- `rivendell/utils.py` (NEW): Safe input wrapper
- `rivendell/main.py`:
  - Removed apfs-fuse runtime check
  - Forced Volatility3 usage
  - Import safe_input
  - Replaced all input() calls with safe_input()
- `rivendell/post/yara.py`:
  - Import safe_input
  - Replaced input() with safe_input()
- `rivendell/mount.py`: Added directory existence checks
- `web/backend/tasks.py` & `tasks_docker.py`:
  - Added ELROND_NONINTERACTIVE environment variable
  - Removed --auto flag requirement

#### Frontend (React)
- `components/OptionsPanel.js`: Error positioning in confirm step
- `components/JobDetails.js`: Filtered internal options, improved formatting
- `components/NewAnalysis.js`: Auto-clear errors on option changes

### Breaking Changes

⚠️ **Docker image rebuild required** - See REBUILD_REQUIRED.md

### Migration Guide

**Quick rebuild using script:**
```bash
./rebuild.sh
```

**Manual rebuild:**
1. Stop all containers: `docker-compose down`
2. Rebuild images: `docker-compose build --no-cache`
3. Start services: `docker-compose up -d`
4. Verify installations:
   - `docker exec rivendell-app which apfs-fuse`
   - `docker exec rivendell-app vol3 --help`

### Bug Fixes
- Fixed hanging jobs caused by interactive prompts
- Fixed shadow_mount directory errors on macOS
- Fixed Navigator validation enforcement
- Fixed directory path handling for E01 files
- Fixed Enabled Options showing internal flags

### Performance
- Reduced startup prompts = faster analysis
- Automatic Volatility3 selection = no user wait time
- Pre-installed tools = no runtime downloads

### Security
- No runtime script downloads
- Verified tool versions in Docker image
- Consistent environment across deployments


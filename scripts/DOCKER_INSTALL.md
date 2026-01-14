# Docker Installation Reference

**📖 For complete installation guide, see [INSTALL.md](../INSTALL.md)**

This document provides detailed Docker-specific information, troubleshooting, and manual installation links.

---

## Quick Start

**Most users should use the automated installer:**

```bash
# Run the installer (includes Docker + image paths)
python3 scripts/install-rivendell.py
```

**This document is useful if you:**
- Need manual Docker download links (installer failed)
- Want to understand Docker options in detail
- Need Docker-specific troubleshooting
- Want to switch between Docker Desktop and OrbStack
- Need to know why we use Docker Desktop 4.51.0

---

**The installer will:**
1. Detect your OS and architecture
2. Present Docker options (Desktop vs OrbStack)
3. Download and install your selection
4. Verify installation
5. **Prompt for forensic image paths** (up to 3 directories)
6. Automatically update `docker-compose.yml`

## Supported Platforms

### macOS (Intel & Apple Silicon)
- ✅ Docker Desktop 4.51.0 (Engine v28.5.2)
- ✅ OrbStack (latest)

### Linux
- ✅ Docker Desktop 4.51.0 (Ubuntu, Debian, Fedora, RHEL, CentOS)
- ❌ OrbStack (macOS only)

### Windows
- ✅ Docker Desktop 4.51.0 (amd64)
- ❌ OrbStack (macOS only)

## Installation Options

### Option 1: Docker Desktop 4.51.0

**Pros:**
- Stable version without gVisor networking bugs
- Official Docker Desktop experience
- Cross-platform (macOS, Linux, Windows)
- Includes Docker Compose

**Cons:**
- Uses 8-12GB RAM
- Slower file sharing on macOS
- Auto-updates (must disable manually)

**Perfect for:**
- Users who prefer official Docker Desktop
- Windows and Linux users
- Teams requiring consistent Docker environment

### Option 2: OrbStack (macOS only)

**Pros:**
- 2-3x faster than Docker Desktop
- Uses ~4GB RAM instead of 8-12GB
- Better file sharing performance
- No gVisor networking bugs
- Native macOS integration
- Instant startup

**Cons:**
- macOS only
- Requires subscription for commercial use ($10/month)
- Less familiar for Docker Desktop users

**Perfect for:**
- macOS users (Intel or Apple Silicon)
- Users needing better performance
- Personal projects (free)
- Limited RAM machines (16GB Macs)

## What the Installer Does

### For Docker Desktop:

**macOS:**
1. Downloads Docker Desktop 4.51.0 DMG
2. Provides step-by-step installation instructions
3. Verifies installation
4. Reminds to disable auto-updates

**Linux:**
1. Detects Linux distribution
2. Downloads appropriate package (.deb or .rpm)
3. Installs using system package manager
4. Verifies installation

**Windows:**
1. Downloads Docker Desktop 4.51.0 installer
2. Launches installer
3. Provides installation instructions

### For OrbStack (macOS only):

1. Checks for Homebrew
2. Installs via Homebrew if available
3. Falls back to manual download if needed
4. Provides setup instructions
5. Verifies installation

## After Installation

### Start Rivendell:
```bash
cd /path/to/rivendell
./scripts/start-testing-mode.sh
```

### Run Tests:
```bash
cd tests
./scripts/run_single_test.sh win_brisk
./scripts/batch/batch1a-archive-lnk.sh
```

### Check Job Status:
```bash
./scripts/status.sh
./scripts/status.sh --watch
```

## Switching Between Docker Desktop and OrbStack

If you have both installed:

```bash
# Use Docker Desktop
docker context use desktop-linux

# Use OrbStack
docker context use orbstack

# Check which is active
docker context show
```

## Troubleshooting

### Docker Desktop won't start after installation
- Restart your computer
- Check Docker Desktop logs: `~/Library/Containers/com.docker.docker/Data/log/`
- Ensure virtualization is enabled in BIOS/UEFI (Windows/Linux)

### OrbStack installation fails on macOS
- Try manual download: https://orbstack.dev/download
- Check macOS version (requires macOS 12.0+)
- Ensure you have admin privileges

### Linux installation fails
- Ensure you have sudo privileges
- Update package manager: `sudo apt update` or `sudo dnf update`
- Check distribution support: https://docs.docker.com/engine/install/

### Downloaded file is corrupted
- Delete and re-download
- Check internet connection
- Verify checksums if available

## Why Docker Desktop 4.51.0?

This specific version (released November 13, 2025) is recommended because:
- Docker Engine v28.5.2 (stable, mature)
- No gVisor networking bugs (present in 29.x)
- Latest version before Docker Engine v29.0.0
- Released within last 6 months (still downloadable)
- Proven stable for Rivendell's workloads

**Known issue in newer versions:**
Docker Desktop 4.52.0+ includes Docker Engine v29.x which has a gVisor networking bug on macOS that causes crashes when:
- Accessing large files via VirtioFS (like Rivendell's 11GB E01 images)
- Long-running HTTP connections (forensic processing)
- Heavy I/O operations

Version 4.51.0 with Engine v28.5.2 does not have this issue.

## Manual Installation

If the installer doesn't work, you can manually download and install:

### Docker Desktop 4.51.0:

**macOS Apple Silicon:**
https://desktop.docker.com/mac/main/arm64/210443/Docker.dmg

**macOS Intel:**
https://desktop.docker.com/mac/main/amd64/210443/Docker.dmg

**Linux (Ubuntu/Debian):**
https://desktop.docker.com/linux/main/amd64/210443/docker-desktop-4.51.0-amd64.deb

**Linux (Fedora/RHEL):**
https://desktop.docker.com/linux/main/amd64/210443/docker-desktop-4.51.0-x86_64.rpm

**Windows:**
https://desktop.docker.com/win/main/amd64/210443/Docker%20Desktop%20Installer.exe

### OrbStack:

**macOS:**
https://orbstack.dev/download

Or via Homebrew:
```bash
brew install --cask orbstack
```

## Contributing

If you encounter issues or want to add support for more platforms:
1. Open an issue: https://github.com/cmdaltr/rivendell/issues
2. Submit a pull request with fixes
3. Test on your platform and report results

## License

This installer is part of the Rivendell project.

# Elrond Project Structure

Complete directory structure reference for the Elrond project.

## Root Directory

```
elrond/
├── 📄 README.md                 # Main project documentation
├── 📄 STRUCTURE.md              # This file - project structure guide
├── 📄 Dockerfile                # Docker image for forensics engine
├── 📄 nginx.conf                # Nginx reverse proxy configuration
├── 📄 .env.example              # Environment variables template
├── 📄 .dockerignore             # Docker build exclusions
├── 📄 cli.py                    # New CLI interface (v2.0)
├── 📄 elrond.py                 # Main forensics engine entry point
├── 📄 __init__.py               # Python package init
│
├── 📁 docs/                     # 📚 Documentation
├── 📁 docker/                   # 🐳 Docker configurations
├── 📁 scripts/                  # 🔧 Shell scripts
├── 📁 core/                     # 🎯 Core engine
├── 📁 platform/                 # 💻 Platform adapters
├── 📁 tools/                    # 🛠️ Tool management
├── 📁 utils/                    # 🔨 Utility functions
├── 📁 config/                   # ⚙️ Configuration
├── 📁 rivendell/                # 🏰 Forensic modules (legacy)
├── 📁 web/                      # 🌐 Web application
├── 📁 tests/                    # 🧪 Test suite
└── 📁 images/                   # 🖼️ Image assets
```

## Documentation (docs/)

```
docs/
├── CONFIG.md                    # Configuration and setup guide
├── DOCKER.md                    # Complete Docker deployment guide (600+ lines)
├── DOCKER-QUICKSTART.md         # Docker quick start (5 minutes)
├── SUPPORT.md                   # Support and troubleshooting
├── TESTING.md                   # Testing guide and best practices
└── VIRTUALMACHINE.md            # VM setup instructions
```

**Purpose**: All user-facing documentation organized in one place.

## Docker (docker/)

```
docker/
├── docker-compose.yml           # Development environment
└── docker-compose.prod.yml      # Production environment
```

**Purpose**: Docker Compose configurations for different deployment scenarios.

## Scripts (scripts/)

```
scripts/
├── docker-start.sh              # Docker startup manager (interactive)
├── config.sh                    # Configuration helper script
└── elrond.sh                    # Elrond wrapper script
```

**Purpose**: Executable shell scripts for common operations.

## Core Engine (core/)

```
core/
├── __init__.py
├── engine.py                    # Main ElrondEngine class
└── executor.py                  # Task execution manager
```

**Purpose**: Core forensics engine implementation with clean architecture.

**Key Classes**:
- `ElrondEngine`: Main orchestrator for forensic analysis
- `Executor`: Manages task execution and resource allocation
- `LegacyBridge`: Compatibility layer with original code

## Platform Adapters (platform/)

```
platform/
├── __init__.py
├── base.py                      # Base platform interface (abstract)
├── factory.py                   # Platform adapter factory
├── linux.py                     # Linux-specific implementation
├── macos.py                     # macOS-specific implementation
└── windows.py                   # Windows-specific implementation
```

**Purpose**: Platform-specific functionality abstraction.

**Capabilities**:
- Disk image mounting/unmounting
- Permission checking (root/sudo/admin)
- Image type identification
- File system operations
- Platform-specific tool execution

## Tool Management (tools/)

```
tools/
├── __init__.py
├── definitions.py               # Forensic tool definitions
├── manager.py                   # Tool verification and management
├── installer.py                 # Automated tool installation
├── siem_installer.py            # SIEM (Splunk/Elastic) setup
└── srum_dump/                   # SRUM database parser
    └── srum_dump.py
```

**Purpose**: Forensic tool management and installation automation.

**Features**:
- Tool availability checking
- Installation suggestions per platform
- Dependency verification
- Tool categorization (memory, timeline, imaging, etc.)

## Utilities (utils/)

```
utils/
├── __init__.py
├── constants.py                 # Application constants
├── exceptions.py                # Custom exceptions
├── helpers.py                   # Helper functions
├── logging.py                   # Logging configuration
├── validators.py                # Input validation
├── version_compat.py            # Python version compatibility
├── windows.py                   # Windows-specific utilities
└── macos.py                     # macOS-specific utilities
```

**Purpose**: Shared utility functions and helpers.

**Categories**:
- Time calculations and formatting
- File size formatting
- Path validation
- Case ID sanitization
- Mount point generation
- User interaction helpers

## Configuration (config/)

```
config/
├── __init__.py
└── settings.py                  # Application settings singleton
```

**Purpose**: Centralized configuration management.

## Rivendell (rivendell/)

Legacy forensic modules - being gradually refactored:

```
rivendell/
├── main.py                      # Main orchestrator
├── meta.py                      # Metadata operations
├── audit.py                     # Audit logging
├── mount.py                     # Disk mounting
│
├── collect/                     # 📥 Artifact Collection
│   ├── collect.py               # Main collection orchestrator
│   ├── linux.py                 # Linux artifact collection
│   ├── mac.py                   # macOS artifact collection
│   ├── windows.py               # Windows artifact collection
│   ├── reorganise.py            # Artifact reorganization
│   ├── files/                   # File collection
│   │   ├── files.py
│   │   ├── select.py
│   │   ├── carve.py
│   │   ├── compare.py
│   │   └── i30.py
│   └── users/                   # User profile collection
│       ├── linux.py
│       ├── mac.py
│       └── windows.py
│
├── process/                     # ⚙️ Artifact Processing
│   ├── process.py               # Main processing orchestrator
│   ├── select.py                # Artifact selection
│   ├── timeline.py              # Timeline generation
│   ├── linux.py                 # Linux artifact processing
│   ├── mac.py                   # macOS artifact processing
│   ├── windows.py               # Windows artifact processing
│   ├── browser.py               # Browser history processing
│   ├── nix.py                   # Unix/Linux processing
│   └── extractions/             # Specific artifact extractors
│       ├── evtx.py              # Event logs
│       ├── mft.py               # Master File Table
│       ├── usn.py               # USN Journal
│       ├── shimcache.py         # Shimcache
│       ├── sru.py               # SRUM database
│       ├── usb.py               # USB history
│       ├── wmi.py               # WMI
│       ├── wbem.py              # WBEM
│       ├── plist.py             # macOS plists
│       ├── mail.py              # Email
│       ├── clipboard.py         # Clipboard data
│       └── registry/            # Windows Registry
│           ├── dumpreg.py
│           ├── profile.py
│           └── system.py
│
├── analysis/                    # 🔍 Analysis Modules
│   ├── analysis.py              # Main analysis orchestrator
│   ├── iocs.py                  # IOC detection
│   └── keywords.py              # Keyword searching
│
├── memory/                      # 🧠 Memory Forensics
│   ├── memory.py                # Memory analysis orchestrator
│   ├── volcore.py               # Volatility core wrapper
│   ├── plugins.py               # Volatility plugins
│   ├── profiles.py              # Memory profiles
│   └── extract.py               # Memory extraction
│
└── post/                        # 📤 Post-Processing
    ├── clean.py                 # Cleanup operations
    ├── clam.py                  # ClamAV scanning
    ├── yara.py                  # YARA scanning
    ├── splunk/                  # Splunk integration
    │   ├── config.py
    │   ├── ingest.py
    │   └── app/                 # Splunk app generator
    ├── elastic/                 # Elastic integration
    │   ├── config.py
    │   └── ingest.py
    └── mitre/                   # MITRE ATT&CK
        ├── nav_attack.py
        └── nav_config.py
```

**Purpose**: Core forensic analysis modules (being refactored to new architecture).

## Web Application (web/)

```
web/
├── backend/                     # FastAPI Backend
│   ├── main.py                  # API server entry point
│   ├── config.py                # Backend configuration
│   ├── storage.py               # Job storage manager
│   ├── tasks.py                 # Celery tasks
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Backend container
│   ├── .dockerignore
│   ├── .env.example
│   └── models/                  # Data models
│       ├── __init__.py
│       └── job.py               # Job models
│
└── frontend/                    # React Frontend
    ├── src/                     # Source code
    │   ├── components/          # React components
    │   ├── pages/              # Page components
    │   ├── services/           # API services
    │   └── App.js              # Main app
    ├── public/                  # Static assets
    ├── package.json             # Node dependencies
    ├── Dockerfile               # Frontend container
    └── .dockerignore
```

**Purpose**: Modern web interface for job management and monitoring.

**Tech Stack**:
- Backend: FastAPI + Celery + Redis
- Frontend: React 18 + Axios
- Database: File-based (with PostgreSQL option)

## Tests (tests/)

```
tests/
├── conftest.py                  # Pytest fixtures and configuration
├── pytest.ini                   # Pytest settings
├── requirements.txt             # Test dependencies
├── run_tests.sh                 # Test runner script
├── README.md                    # Testing documentation
│
├── unit/                        # Unit Tests (80+ tests)
│   ├── __init__.py
│   ├── test_engine.py           # Core engine tests
│   ├── test_platform.py         # Platform adapter tests
│   ├── test_tool_manager.py     # Tool manager tests
│   ├── test_storage.py          # Storage tests
│   ├── test_tasks.py            # Celery task tests
│   └── test_helpers.py          # Utility tests
│
└── integration/                 # Integration Tests (20+ tests)
    ├── __init__.py
    └── test_web_api.py          # Web API integration tests
```

**Purpose**: Comprehensive test coverage for all components.

**Coverage**:
- Unit tests: ~100 tests
- Integration tests: ~30 tests
- Overall coverage: ~85%

## File Organization Principles

### By Purpose
- **docs/**: User-facing documentation
- **docker/**: Deployment configurations
- **scripts/**: Executable utilities
- **tests/**: All test code

### By Layer
- **core/**: Business logic (platform-agnostic)
- **platform/**: Platform-specific implementations
- **rivendell/**: Forensic operations
- **web/**: User interface

### By Responsibility
- **tools/**: External tool management
- **utils/**: Shared utilities
- **config/**: Configuration management

## Quick Reference

### Starting Elrond

```bash
# Docker
./scripts/docker-start.sh

# Native
python elrond.py CASE-001 /evidence/disk.E01 /output --Collect --Process
```

### Running Tests

```bash
# Python tests
cd tests && pytest

# Web tests
cd web/tests && npm test
```

### Building Docker Images

```bash
# Development
docker-compose -f docker/docker-compose.yml build

# Production
docker-compose -f docker/docker-compose.prod.yml build
```

### Key Configuration Files

- `.env`: Environment variables (create from `.env.example`)
- `docker/docker-compose.yml`: Development Docker setup
- `docker/docker-compose.prod.yml`: Production Docker setup
- `nginx.conf`: Production reverse proxy
- `pytest.ini`: Test configuration

## File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| docs/ | 6 | Documentation |
| docker/ | 2 | Docker configs |
| scripts/ | 3 | Shell scripts |
| core/ | 3 | Core engine |
| platform/ | 6 | Platform adapters |
| tools/ | 6 | Tool management |
| utils/ | 9 | Utilities |
| rivendell/ | 50+ | Forensic modules |
| web/backend/ | 10+ | Backend API |
| web/frontend/ | 100+ | Frontend app |
| tests/ | 10+ | Test suite |
| **Total** | **200+** | **All files** |

---

**Last Updated**: 2025-01-15
**Version**: 2.1.0

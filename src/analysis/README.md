# Elrond - Digital Forensics Automation Tool

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/cmdaltr/elrond)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

**Elrond** is a comprehensive digital forensics automation tool designed to streamline the analysis of disk images, memory dumps, and digital evidence. Named after the wise Elven lord from Middle-earth, Elrond brings wisdom and power to forensic investigations.

## 🎯 Features

### Core Capabilities
- ✅ **Automated Forensic Analysis**: Full-stack automation for disk and memory forensics
- ✅ **Multi-Platform Support**: Linux, macOS, and Windows analysis capabilities
- ✅ **Web Interface**: Modern React-based UI for job management and monitoring
- ✅ **CLI Interface**: Powerful command-line interface for advanced users
- ✅ **Docker Support**: Fully containerized deployment option
- ✅ **Distributed Processing**: Celery-based background task execution

### Forensic Tools Integration
- **Disk Imaging**: E01, RAW, DD, VMDK, VHD/VHDX support
- **Memory Analysis**: Volatility 3 integration
- **Timeline Analysis**: Plaso (log2timeline) integration
- **Registry Analysis**: Windows registry parsing and analysis
- **Event Log Analysis**: EVTX parsing and correlation
- **File System Analysis**: MFT, USN Journal, $I30 index analysis
- **Artifact Extraction**: Browser history, prefetch, shimcache, SRUM, and more

### Analysis Features
- 📊 **Timeline Generation**: Comprehensive timeline analysis with Plaso
- 🧠 **Memory Forensics**: Full Volatility 3 plugin suite
- 🔍 **IOC Detection**: YARA rules and keyword searching
- 🗂️ **Artifact Collection**: Automated collection of key forensic artifacts
- 📈 **MITRE ATT&CK Mapping**: Comprehensive content-based technique detection with 600+ techniques, multi-tactic support, and ATT&CK Navigator visualization
- 🔐 **Malware Detection**: ClamAV integration for malware scanning
- 📤 **SIEM Export**: Direct export to Splunk and Elastic

## 📁 Project Structure

```
elrond/
├── cli.py                   # Command-line interface
├── elrond.py               # Main forensics engine entry point
├── Dockerfile              # Docker image for forensics engine
├── .env.example            # Environment variable template
├── .dockerignore           # Docker build exclusions
├── nginx.conf              # Nginx configuration for production
│
├── docs/                   # 📚 Documentation
│   ├── CONFIG.md          # Configuration guide
│   ├── DOCKER.md          # Docker deployment guide (detailed)
│   ├── DOCKER-QUICKSTART.md # Docker quick start
│   ├── SUPPORT.md         # Support and troubleshooting
│   ├── TESTING.md         # Testing guide
│   └── VIRTUALMACHINE.md  # VM setup guide
│
├── docker/                 # 🐳 Docker Configuration
│   ├── docker-compose.yml      # Development stack
│   └── docker-compose.prod.yml # Production stack
│
├── scripts/                # 🔧 Shell Scripts
│   ├── config.sh          # Configuration script
│   ├── elrond.sh          # Elrond wrapper script
│   └── docker-start.sh    # Docker startup manager
│
├── core/                   # 🎯 Core Engine
│   ├── engine.py          # Main forensics engine
│   ├── executor.py        # Task executor
│   └── __init__.py
│
├── platform/               # 💻 Platform Adapters
│   ├── base.py            # Base platform interface
│   ├── factory.py         # Platform factory
│   ├── linux.py           # Linux adapter
│   ├── macos.py           # macOS adapter
│   └── windows.py         # Windows adapter
│
├── tools/                  # 🛠️ Tool Management
│   ├── definitions.py     # Forensic tool definitions
│   ├── manager.py         # Tool manager
│   ├── installer.py       # Tool installer
│   └── siem_installer.py  # SIEM setup
│
├── utils/                  # 🔨 Utilities
│   ├── helpers.py         # Helper functions
│   ├── logging.py         # Logging configuration
│   ├── validators.py      # Input validators
│   └── constants.py       # Constants and enums
│
├── config/                 # ⚙️ Configuration
│   ├── settings.py        # Application settings
│   └── __init__.py
│
├── rivendell/             # 🏰 Forensic Modules (Legacy)
│   ├── main.py            # Main orchestrator
│   ├── collect/           # Artifact collection
│   ├── process/           # Artifact processing
│   ├── analysis/          # Analysis modules
│   ├── memory/            # Memory forensics
│   └── post/              # Post-processing
│
├── web/                    # 🌐 Web Application
│   ├── backend/           # FastAPI backend
│   │   ├── main.py        # API server
│   │   ├── models/        # Data models
│   │   ├── storage.py     # Job storage
│   │   ├── tasks.py       # Celery tasks
│   │   ├── config.py      # Backend config
│   │   ├── Dockerfile     # Backend container
│   │   └── requirements.txt
│   │
│   └── frontend/          # React frontend
│       ├── src/           # Source code
│       ├── public/        # Static files
│       ├── Dockerfile     # Frontend container
│       └── package.json
│
└── tests/                  # 🧪 Test Suite
    ├── conftest.py        # Test fixtures
    ├── pytest.ini         # Pytest config
    ├── requirements.txt   # Test dependencies
    ├── unit/              # Unit tests
    └── integration/       # Integration tests
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/cmdaltr/elrond.git
cd elrond

# Start with Docker (easiest)
./scripts/docker-start.sh

# Or manually
docker-compose -f docker/docker-compose.yml up
```

Access the application:
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api/health

### Option 2: Native Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Check dependencies
python cli.py --check-dependencies

# Install forensic tools
python cli.py --install

# Run analysis
python elrond.py CASE-001 /path/to/image.E01 /output --Collect --Process --quick
```

## 📖 Usage

### Web Interface

1. Navigate to http://localhost:3000
2. Click **"New Analysis"**
3. Select disk image from file browser
4. Configure analysis options
5. Start analysis and monitor progress

### Command Line Interface

```bash
# Basic usage
python elrond.py <CASE_ID> <SOURCE_PATH> [DESTINATION] [OPTIONS]

# Examples:

# Quick analysis
python elrond.py INC-2025-001 /evidence/disk.E01 /output \
  --Collect --Process --quick --Userprofiles

# Comprehensive analysis
python elrond.py INC-2025-001 /evidence/disk.E01 /output \
  --eXhaustive --Collect

# Memory analysis
python elrond.py MEM-2025-001 /evidence/memory.mem /output \
  --Memory --memorytimeline

# With SIEM export
python elrond.py INC-2025-001 /evidence/disk.E01 /output \
  --Collect --Process --Splunk --Navigator
```

### Common Options

- `-C, --Collect`: Collect artifacts from disk image
- `-P, --Process`: Process collected artifacts
- `-A, --Analysis`: Conduct automated forensic analysis
- `-M, --Memory`: Analyze memory dumps with Volatility
- `-T, --Timeline`: Create timeline with Plaso
- `-U, --Userprofiles`: Collect user profile artifacts
- `-S, --Splunk`: Export to Splunk
- `-E, --Elastic`: Export to Elasticsearch
- `-B, --Brisk`: Quick mode with common options
- `-X, --eXhaustive`: Comprehensive analysis (all flags)
- `-q, --quick`: Quick mode (skip hashing/entropy)

### Non-Interactive Mode (Web/Automation)

**Elrond runs in non-interactive mode by default** when used in Docker or web environments. This provides:

- ✅ Clean output without ANSI colors or ASCII art
- ✅ No interactive prompts (uses safe defaults)
- ✅ Perfect for web job logs and automation

The `ELROND_NONINTERACTIVE=1` environment variable is automatically set in Docker. To use interactive CLI mode:

```bash
export ELROND_NONINTERACTIVE=0
python elrond.py CASE-001 /evidence/disk.E01 /output --Collect
```

## 🐳 Docker Usage

### Development

```bash
# Start all services
./scripts/docker-start.sh

# Or with options
./scripts/docker-start.sh --build --detached

# View logs
./scripts/docker-start.sh --logs

# Stop services
./scripts/docker-start.sh --stop
```

### Production

```bash
# Configure environment
cp .env.example .env
# Edit .env with production settings

# Deploy
./scripts/docker-start.sh --prod --build --detached

# Monitor
docker-compose -f docker/docker-compose.prod.yml logs -f
```

See [docs/DOCKER.md](docs/DOCKER.md) for comprehensive Docker documentation.

## 🧪 Testing

Elrond includes comprehensive test suites for both Python and web components.

### Python Tests

```bash
cd tests

# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=elrond --cov-report=html

# Or use the test runner
./run_tests.sh --all --coverage
```

### Web Tests

```bash
cd web/tests

# Install dependencies
npm install
npx playwright install --with-deps

# Run all tests
npm test

# Run with UI
npm run test:ui
```

See [docs/TESTING.md](docs/TESTING.md) for detailed testing documentation.

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[CONFIG.md](docs/CONFIG.md)** - Configuration and setup guide
- **[DOCKER.md](docs/DOCKER.md)** - Complete Docker deployment guide
- **[DOCKER-QUICKSTART.md](docs/DOCKER-QUICKSTART.md)** - Quick Docker setup
- **[TESTING.md](docs/TESTING.md)** - Testing guide and best practices
- **[SUPPORT.md](docs/SUPPORT.md)** - Support and troubleshooting
- **[VIRTUALMACHINE.md](docs/VIRTUALMACHINE.md)** - VM setup instructions

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Security
SECRET_KEY=your-secret-key-here
REDIS_PASSWORD=your-redis-password

# Debug mode
DEBUG=false

# Analysis settings
MAX_CONCURRENT_ANALYSES=3
ANALYSIS_TIMEOUT=86400

# Storage
ALLOWED_PATHS=/evidence,/mnt,/media
```

### Tool Installation

```bash
# Check tool availability
python cli.py --check-dependencies

# Interactive installation
python cli.py --install --interactive

# Install required tools only
python cli.py --install --required-only
```

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/cmdaltr/elrond.git
cd elrond

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt

# Install pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Python tests
cd tests && pytest

# Web backend tests
cd web/backend && pytest

# Web frontend tests
cd web/frontend && npm test

# Integration tests
cd tests && pytest -m integration
```

### Code Style

```bash
# Format code
black .
isort .

# Lint code
flake8 .
pylint elrond/

# Type checking
mypy elrond/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- All tests pass
- Code follows style guidelines
- Documentation is updated
- Commit messages are descriptive

## 🔒 Security

Elrond is designed for defensive security and forensic analysis only. Please:
- Do not use for malicious purposes
- Report security vulnerabilities responsibly
- Follow ethical forensic practices
- Respect privacy and legal requirements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Volatility Foundation** - Memory forensics framework
- **Plaso Project** - Timeline analysis tool
- **The Sleuth Kit** - File system analysis
- **FastAPI** - Modern web framework
- **React** - Frontend framework
- **Tolkien** - For the inspiration and naming

## 📞 Support

For issues, questions, or contributions:

- **GitHub Issues**: [Report a bug](https://github.com/cmdaltr/elrond/issues)
- **Documentation**: See [docs/SUPPORT.md](docs/SUPPORT.md)
- **Discussions**: [GitHub Discussions](https://github.com/cmdaltr/elrond/discussions)

## 🗺️ Roadmap

### v2.2.0 (Planned)
- [ ] Cloud storage support (AWS S3, Azure Blob)
- [ ] Distributed analysis across multiple nodes
- [ ] Advanced machine learning for anomaly detection
- [ ] Mobile device forensics support
- [ ] Encrypted disk image support

### v2.3.0 (Planned)
- [ ] Real-time analysis streaming
- [ ] Collaborative investigation features
- [ ] Advanced reporting engine
- [ ] Plugin system for custom analyzers

## 📊 Project Stats

- **Lines of Code**: ~50,000+
- **Tests**: 290+ test cases
- **Test Coverage**: ~85%
- **Supported Platforms**: Linux, macOS, Windows
- **Docker Images**: 3 (engine, backend, frontend)
- **Documentation Pages**: 6

---

**Made with ⚔️ by forensic investigators, for forensic investigators**

*"Not all those who wander are lost, but their artifacts shall be found." - Gandalf (probably)*

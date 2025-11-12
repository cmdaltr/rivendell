# Rivendell DFIR Suite

```
    ____  _                     __     ____
   |  _ \(_)_   _____ _ __   __| | ___| | |
   | |_) | \ \ / / _ \ '_ \ / _` |/ _ \ | |
   |  _ <| |\ V /  __/ | | | (_| |  __/ | |
   |_| \_\_| \_/ \___|_| |_|\__,_|\___|_|_|

   Digital Forensics Suite v2.0.0
```

**Rivendell** is a unified digital forensics platform that combines remote forensic acquisition and automated analysis capabilities into a single, powerful suite.

## Overview

Rivendell merges two complementary DFIR tools:

- **Gandalf** 🧙 - Remote forensic artifact acquisition tool
- **Elrond** 🏛️ - Automated forensic analysis engine

Together, they provide an end-to-end solution for collecting evidence from remote hosts and performing comprehensive forensic analysis with SIEM integration.

## Features

### 🚀 Acquisition (Gandalf)

- **Multi-Platform Support**: Windows (PowerShell), Linux/macOS (Python + Bash)
- **Remote Acquisition**: SSH and PowerShell remoting
- **Encryption**: Key-based or password-based encryption
- **Memory Dumps**: Live memory acquisition support
- **Comprehensive Collection**: System artifacts, logs, registry, browser data, user profiles
- **Audit Logging**: SHA256 hashing and audit trails for all artifacts

### 🔍 Analysis (Elrond)

- **Automated Analysis**: Artifact collection, processing, and analysis
- **Multi-OS Support**: Windows, Linux, and macOS artifacts
- **Timeline Generation**: Plaso (log2timeline) integration
- **Memory Forensics**: Volatility 3 support
- **IOC Detection**: Automated indicator of compromise extraction
- **SIEM Integration**: Direct export to Splunk and Elasticsearch
- **MITRE ATT&CK Mapping**: Automatic technique identification
- **Multiple Output Formats**: CSV, JSON, timeline formats

### 🌐 Web Interface

- **Modern UI**: React-based web interface
- **RESTful API**: FastAPI backend
- **Job Management**: Track acquisition and analysis jobs
- **Real-time Updates**: WebSocket support for live progress
- **Results Visualization**: Browse and export analysis results

### 🐳 Deployment Options

- **Docker**: Full containerized deployment
- **Docker Compose**: Multi-service orchestration
- **Standalone**: Direct Python/uvicorn execution
- **CLI**: Command-line interface for scripting

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/rivendell.git
cd rivendell

# Start with Docker Compose
docker-compose up -d

# Access web interface
open http://localhost:8000

# View API documentation
open http://localhost:8000/docs
```

### Using uvicorn

```bash
# Install dependencies
pip install -e ".[web]"

# Start web server
python3 -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the CLI
python3 cli/rivendell.py web --port 8000 --reload
```

### Using CLI Tools

```bash
# Install dependencies
pip install -e .

# Acquire from local system
sudo python3 acquisition/python/gandalf.py Password Local -M -o /evidence

# Acquire from remote host (bash version)
sudo bash acquisition/bash/gandalf.sh Password Remote -h 192.168.1.100 -u analyst -m

# Analyze acquired evidence
python3 analysis/elrond.py CASE-001 /evidence/hostname.tar.gz /output -CPAS

# Use unified CLI
python3 cli/rivendell.py acquire Password Local -m
python3 cli/rivendell.py analyze CASE-001 /evidence /output -CPA
```

## Architecture

```
rivendell/
├── acquisition/          # Gandalf - Forensic acquisition tools
│   ├── windows/         # PowerShell scripts for Windows
│   ├── python/          # Python scripts for Linux/macOS
│   ├── bash/            # Pure bash implementation
│   ├── tools/           # Memory dumpers, config scripts
│   └── lists/           # Host and file lists
├── analysis/            # Elrond - Forensic analysis engine
│   ├── core/           # Core analysis engine
│   ├── rivendell/      # Legacy analysis modules
│   ├── collectors/     # Artifact collectors
│   ├── processors/     # Artifact processors
│   └── analyzers/      # Analysis modules
├── web/                # Web interface
│   ├── backend/        # FastAPI REST API
│   └── frontend/       # React UI
├── cli/                # Command-line interfaces
├── docker/             # Docker configurations
├── config/             # Configuration files
├── docs/               # Documentation
└── tests/              # Test suites
```

## Installation

### Prerequisites

**System Requirements:**
- Python 3.8+
- Root/Administrator privileges (for acquisition)
- Docker and Docker Compose (for containerized deployment)

**For Acquisition:**
- Linux/macOS: SSH access, standard Unix tools
- Windows: PowerShell 5.1+, PSRemoting enabled

**For Analysis:**
- The Sleuth Kit (TSK)
- Volatility 3
- Plaso (log2timeline)
- YARA
- ClamAV (optional)
- ExifTool

### Installation Options

#### 1. Docker Installation (Recommended)

```bash
git clone https://github.com/yourusername/rivendell.git
cd rivendell
docker-compose up -d
```

#### 2. Python Installation

```bash
git clone https://github.com/yourusername/rivendell.git
cd rivendell

# Install base dependencies
pip install -e .

# Install with web interface
pip install -e ".[web]"

# Install all dependencies
pip install -e ".[all]"
```

#### 3. Development Installation

```bash
git clone https://github.com/yourusername/rivendell.git
cd rivendell

# Install development dependencies
pip install -e ".[dev,web]"

# Run tests
pytest
```

## Usage

### Acquisition (Gandalf)

#### Windows (PowerShell)

```powershell
# Local acquisition with encryption
.\acquisition\windows\Invoke-Gandalf.ps1 Password Local -Memory

# Remote acquisition
.\acquisition\windows\Invoke-Gandalf.ps1 Key HOSTNAME -OutputDirectory D:\ -Memory
```

#### Linux/macOS (Python)

```bash
# Local acquisition with key encryption and memory dump
sudo python3 acquisition/python/gandalf.py Key Local -M -O /evidence

# Remote acquisition from multiple hosts
sudo python3 acquisition/python/gandalf.py Password Remote -f acquisition/lists/hosts.list -M
```

#### Pure Bash (Linux/Unix)

```bash
# Local acquisition
sudo bash acquisition/bash/gandalf.sh None Local -o /evidence -m

# Remote acquisition
sudo bash acquisition/bash/gandalf.sh Password Remote -h 192.168.1.100 -u analyst -m
```

### Analysis (Elrond)

```bash
# Full analysis with Splunk export
python3 analysis/elrond.py CASE-001 /evidence/hostname.tar.gz /output -CPAS

# Quick analysis (Brisk mode)
python3 analysis/elrond.py CASE-001 /evidence /output -B

# Memory analysis only
python3 analysis/elrond.py MEM-001 /evidence/memory.mem /output -MP

# With YARA and keyword scanning
python3 analysis/elrond.py CASE-001 /evidence /output -CPA -Y /yara/rules -K /keywords.txt
```

### Web Interface

```bash
# Start development server
python3 -m uvicorn web.backend.main:app --reload

# Using CLI
python3 cli/rivendell.py web --port 8000 --reload

# Using Docker
docker-compose up rivendell

# Production with nginx
docker-compose --profile production up
```

### Unified CLI

```bash
# Show help
python3 cli/rivendell.py --help

# Acquire evidence
python3 cli/rivendell.py acquire Password Local -m -o /evidence

# Analyze evidence
python3 cli/rivendell.py analyze CASE-001 /evidence/hostname.tar.gz /output -CPA

# Start web interface
python3 cli/rivendell.py web --port 8000
```

## Configuration

### Remote Acquisition Setup

#### SSH (Linux/macOS)

```bash
# Enable SSH on target hosts
sudo systemctl enable ssh
sudo systemctl start ssh

# Configure firewall
sudo ufw allow 22/tcp
```

#### PowerShell Remoting (Windows)

```powershell
# Enable PowerShell remoting on target
Enable-PSRemoting -Force

# Add acquisition host to TrustedHosts
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "ACQUISITION_HOST" -Force
```

### Host Lists

Create `acquisition/lists/hosts.list`:
```
# One hostname or IP per line
192.168.1.100
WORKSTATION01
SERVER02
```

### File Collection Lists

Create `acquisition/lists/files.list`:
```
# File patterns to collect
*.docx
*.pdf
important_file.txt
```

## Docker Deployment

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Build production image
docker-compose build --target production

# Start with nginx reverse proxy
docker-compose --profile production up -d

# Scale workers
docker-compose up -d --scale celery-worker=4
```

### Services

- **rivendell**: Main application (port 8000)
- **redis**: Caching and Celery broker (port 6379)
- **postgres**: Metadata storage (port 5432)
- **celery-worker**: Background task processing
- **flower**: Celery monitoring (port 5555)
- **nginx**: Reverse proxy (ports 80, 443)

## Output Formats

### Acquisition Output

```
hostname.tar.gz[.enc]
├── artefacts/
│   ├── host.info
│   ├── process.info
│   ├── memory/
│   ├── logs/
│   ├── browsers/
│   └── user/
├── log.audit         # CSV audit log
└── log.meta          # SHA256 hashes
```

### Analysis Output

```
CASE-001/
├── collected/        # Collected artifacts
├── processed/        # Processed data (CSV/JSON)
├── timeline/         # Timeline analysis
├── analysis/         # IOCs, keywords
├── splunk/          # Splunk exports (optional)
├── elastic/         # Elasticsearch exports (optional)
└── reports/         # Summary reports
```

## SIEM Integration

### Splunk

```bash
# Analyze and export to Splunk
python3 analysis/elrond.py CASE-001 /evidence /output -CPAS

# Splunk output includes:
# - HEC-compatible JSON events
# - MITRE ATT&CK mappings
# - Custom app configuration
# - Index configuration
```

### Elasticsearch

```bash
# Analyze and export to Elasticsearch
python3 analysis/elrond.py CASE-001 /evidence /output -CPAE

# Elasticsearch output includes:
# - Bulk API JSON format
# - Index templates
# - Field mappings
# - Kibana dashboards (coming soon)
```

## Advanced Features

### Memory Forensics

```bash
# Full memory analysis with Volatility 3
python3 analysis/elrond.py MEM-001 /memory.mem /output -MP

# Supported plugins:
# - Process listings
# - Network connections
# - Loaded drivers
# - Registry keys
# - File handles
```

### YARA Scanning

```bash
# Scan with YARA rules
python3 analysis/elrond.py CASE-001 /evidence /output -CPA -Y /path/to/yara/rules/
```

### Keyword Searching

```bash
# Search for keywords
python3 analysis/elrond.py CASE-001 /evidence /output -CPA -K /path/to/keywords.txt
```

### ClamAV Malware Scanning

```bash
# Enable malware scanning
python3 analysis/elrond.py CASE-001 /evidence /output -CPA --clam
```

## API Documentation

When running the web interface, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=acquisition --cov=analysis --cov=web

# Run specific tests
pytest tests/test_acquisition.py
```

### Code Style

```bash
# Format code with black
black .

# Lint with flake8
flake8 acquisition/ analysis/ web/ cli/

# Type checking with mypy
mypy acquisition/ analysis/ web/ cli/
```

## Troubleshooting

### Acquisition Issues

**Permission Denied:**
```bash
# Ensure running as root/administrator
sudo python3 acquisition/python/gandalf.py ...
```

**SSH Connection Failed:**
```bash
# Test SSH connectivity
ssh user@hostname

# Check SSH config
cat ~/.ssh/config
```

**PowerShell Remoting Failed:**
```powershell
# Test remoting
Test-WSMan HOSTNAME

# Check TrustedHosts
Get-Item WSMan:\localhost\Client\TrustedHosts
```

### Analysis Issues

**Tool Not Found:**
```bash
# Check dependencies
python3 analysis/cli.py --check-dependencies

# Install tools
python3 analysis/cli.py --install
```

**Memory Analysis Failed:**
```bash
# Ensure Volatility 3 is installed
pip install volatility3
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTION.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgements

This project combines and extends:
- **Gandalf** - Remote forensic acquisition tool
- **Elrond** - Automated forensic analysis engine

Built upon excellent open-source tools:
- The Sleuth Kit
- Volatility Foundation
- Plaso (log2timeline)
- YARA
- FastAPI
- React

Special thanks to the DFIR community and all contributors.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/rivendell/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rivendell/discussions)

## Roadmap

- [ ] Enhanced web UI with job scheduling
- [ ] Additional artifact parsers
- [ ] Cloud platform acquisition (AWS, Azure, GCP)
- [ ] Automated threat hunting playbooks
- [ ] Machine learning-based IOC detection
- [ ] Kibana dashboard templates
- [ ] Mobile device acquisition support

---

**Rivendell DFIR Suite** - Where Evidence Meets Analysis 🧙‍♂️⚔️🏛️

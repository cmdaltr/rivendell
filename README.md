# Rivendell DFIR Suite

<div align="center">
  <img src="./docs/images/rivendell.png" alt="Rivendell - The Last Homely House" width="800"/>

  **Digital Forensics Suite v2.1.0**
</div>

**Rivendell** is a comprehensive digital forensics and incident response (DFIR) platform that combines remote acquisition, automated analysis, AI-powered investigation, and cloud forensics capabilities into a unified suite.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

---

## 🌟 Key Features

### 🔍 Comprehensive Forensics Platform

- **Remote Acquisition** - Collect artifacts from remote Windows, Linux, and macOS systems
- **Automated Analysis** - Process evidence with 30+ integrated forensic tools
- **MITRE ATT&CK Integration** - Automatic technique mapping and coverage analysis
- **Cloud Forensics** - AWS, Azure, and GCP investigation support
- **AI-Powered Analysis** - Natural language queries of investigation data
- **Memory Forensics** - Volatility 3 integration for memory analysis
- **Timeline Generation** - Plaso/log2timeline for comprehensive timelines
- **SIEM Integration** - Direct export to Splunk and Elasticsearch

### 🎯 Core Components

```
┌──────────────────────────────────────────────────────┐
│                     Rivendell Suite                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐   ┌───────────┐  │
│  │   Gandalf    │  │    Elrond    │   │    AI     │  │
│  │ Acquisition  │→ │   Analysis   │ → │  Agent    │  │
│  └──────────────┘  └──────────────┘   └───────────┘  │
│         ↓                  ↓               ↓         │
│  ┌───────────────────────────────────────────────┐   │
│  │     MITRE ATT&CK • Cloud • SIEM • Reports     │   │
│  └───────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/rivendell.git
cd rivendell

# Linux
sudo ./scripts/install_linux.sh

# macOS
./scripts/install_macos.sh

# Windows (WSL2)
.\scripts\install_windows_wsl.ps1

# Verify installation
elrond --check-dependencies
```

### Basic Usage

**Complete Investigation Workflow:**

```bash
# 1. Acquire evidence from remote system
python3 acquisition/python/gandalf.py Password 192.168.1.100 \
  -u administrator -M -o /evidence/CASE-001

# 2. Process and analyze evidence
elrond -C -c CASE-001 \
  -s /evidence/CASE-001 \
  -m /evidence/CASE-001/memory.dmp \
  -o /cases/CASE-001

# 3. Map to MITRE ATT&CK
python3 -m rivendell.mitre.mapper /cases/CASE-001

# 4. Index for AI analysis
rivendell-ai index CASE-001 /cases/CASE-001

# 5. Query with natural language
rivendell-ai query CASE-001 "What PowerShell commands were executed?"

# 6. Generate report
rivendell-ai summary CASE-001 --format markdown --output report.md
```

---

## 📋 Features Overview

### Gandalf - Remote Acquisition

Collect forensic artifacts from local and remote systems.

**Features:**
- Multi-platform support (Windows, Linux, macOS)
- Remote acquisition via SSH and PowerShell
- Memory dump collection
- Encrypted evidence packaging
- SHA256 hashing and audit trails
- Comprehensive artifact collection

**Usage:**
```bash
# Local acquisition
sudo python3 acquisition/python/gandalf.py Password Local -M -o /evidence

# Remote Windows system
python3 acquisition/python/gandalf.py Password 192.168.1.100 -u admin -M -o /evidence

# Remote Linux system via SSH
python3 acquisition/python/gandalf.py Password 192.168.1.100 -u root -M -o /evidence
```

**Collected Artifacts:**
- System information
- Running processes
- Network connections
- Registry hives (Windows)
- Event logs (Windows)
- System logs (Linux/macOS)
- Browser artifacts
- User profiles
- Scheduled tasks
- Services
- Memory dumps

[Full Documentation →](docs/gandalf-README.md)

---

### Elrond - Automated Analysis

Process and analyze forensic evidence with integrated tools.

**Features:**
- Automated artifact parsing
- Timeline generation with Plaso
- Memory forensics with Volatility 3
- Registry analysis
- Event log parsing
- IOC detection
- Browser artifact extraction
- Multi-OS support (Windows, Linux, macOS)

**Usage:**
```bash
# Process evidence (Collect mode)
elrond -C -c CASE-001 -s /evidence -o /output

# Analyze existing extraction (Gandalf mode)
elrond -G -c CASE-001 -s /extracted_data -o /output

# With memory analysis
elrond -C -c CASE-001 -s /evidence -m /memory.dmp -o /output

# Timeline generation
elrond -C -c CASE-001 -s /evidence -t -o /output
```

**Integrated Tools:**
- Volatility 3 (memory analysis)
- Plaso/log2timeline (timeline generation)
- RegRipper (registry parsing)
- EvtxCmd (event log parsing)
- Bulk Extractor (IOC extraction)
- 25+ additional forensic utilities

[Full Documentation →](docs/elrond-README.md)

---

### Feature 1: MITRE ATT&CK Integration

Automatically map forensic findings to MITRE ATT&CK techniques.

**Features:**
- Auto-updates from MITRE ATT&CK framework
- Technique mapping for 100+ techniques
- ATT&CK matrix dashboard generation
- Coverage analysis and gap identification
- Integration with analysis pipeline

**Usage:**
```bash
# Update MITRE data
python3 -m rivendell.mitre.updater

# Map artifacts to techniques
python3 -m rivendell.mitre.mapper /path/to/artifacts

# Generate dashboard
python3 -m rivendell.mitre.dashboard -o /output/dashboard.html
```

**Coverage:**
- 100+ ATT&CK techniques detected
- All 14 tactics covered
- Automatic technique identification
- Evidence source mapping

[Full Documentation →](docs/USER_GUIDE.md#feature-1-mitre-attack-integration)

---

### Feature 2: Coverage Analysis

Real-time MITRE ATT&CK coverage analysis during investigations.

**Features:**
- Standalone coverage analyzer
- Live detection as artifacts are processed
- Integration with Elrond analysis
- SIEM export (Splunk, Elasticsearch)
- Visual coverage dashboards

**Usage:**
```bash
# Analyze coverage
python3 -m rivendell.coverage.analyzer /cases/CASE-001

# Real-time monitoring
python3 -m rivendell.coverage.monitor --watch /cases

# Generate dashboard
python3 -m rivendell.coverage.dashboard -o dashboard.html
```

[Full Documentation →](docs/USER_GUIDE.md#feature-2-coverage-analysis)

---

### Feature 3: Enhanced Artifact Parsing

Extended support for Windows, macOS, and Linux artifacts.

**Features:**
- **Windows**: WMI persistence detection, scheduled tasks, services
- **macOS**: plists, launch agents/daemons, unified logs, FSEvents
- **Linux**: systemd services, cron jobs, bash history, auth logs

**Usage:**
```bash
# Parse Windows WMI
python3 -m rivendell.artifacts.windows.wmi /path/to/system

# Parse macOS artifacts
python3 -m rivendell.artifacts.macos.launch_agents /path/to/system

# Parse Linux artifacts
python3 -m rivendell.artifacts.linux.systemd /path/to/system
```

[Full Documentation →](docs/ARTIFACTS.md)

---

### Feature 4: Cloud Forensics

Investigate cloud infrastructure across AWS, Azure, and GCP.

**Features:**
- **AWS**: EC2 snapshots, CloudTrail analysis, S3 forensics
- **Azure**: VM disk snapshots, Activity Log analysis
- **GCP**: Compute Engine snapshots, Cloud Logging analysis
- Unified CLI across all providers
- MITRE ATT&CK mapping for cloud techniques

**Usage:**
```bash
# List AWS instances
python3 -m rivendell.cloud.cli aws list --credentials aws_creds.json

# Acquire Azure VM disk
python3 -m rivendell.cloud.cli azure acquire-disk \
  --instance-id myvm \
  --resource-group mygroup \
  --output ./output

# Analyze CloudTrail logs
python3 -m rivendell.cloud.cli aws analyze-logs \
  --log-file cloudtrail.json \
  --output ./analysis
```

**Detected Techniques:**
- T1078.004 - Cloud Accounts
- T1530 - Data from Cloud Storage
- T1580 - Cloud Infrastructure Discovery
- T1619 - Cloud Storage Object Discovery
- And 13+ more cloud-specific techniques

[Full Documentation →](docs/CLOUD.md)

---

### Feature 5: AI-Powered Analysis Agent

Query investigation data using natural language with local AI.

**Features:**
- Natural language queries of forensic data
- Investigation path suggestions
- Automated case summaries
- Web chat interface (port 5687)
- Privacy-focused local LLM (Ollama/LlamaCpp)
- Multi-artifact search (timeline, IOCs, processes, network, registry)

**Usage:**
```bash
# Index case data
rivendell-ai index CASE-001 /cases/CASE-001

# Query the case
rivendell-ai query CASE-001 "What PowerShell commands were executed?"

# Get investigation suggestions
rivendell-ai suggest CASE-001

# Generate case summary
rivendell-ai summary CASE-001 --format markdown --output summary.md

# Start web interface
python3 -m rivendell.ai.web_interface
# Access at http://localhost:5687/ai/chat/CASE-001
```

**Example Queries:**
- "What PowerShell commands were executed?"
- "Show network connections to external IPs"
- "What MITRE ATT&CK techniques were detected?"
- "Summarize the attack timeline"
- "What persistence mechanisms were found?"

[Full Documentation →](docs/AI_AGENT.md)

---

## 🛠️ Installation Requirements

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB
- Python 3.8+

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- GPU: NVIDIA GPU with 8GB+ VRAM (for AI features)
- Storage: 100+ GB NVMe/SSD

### Dependencies

**Core Tools:**
- Python 3.8+
- Volatility 3
- Plaso/log2timeline
- 30+ forensic utilities

**Optional:**
- Ollama (for AI agent)
- Docker (for containerized deployment)
- Splunk/Elasticsearch (for SIEM integration)

**See:** [TOOLS.md](docs/TOOLS.md)

---

## 📚 Documentation

### User Documentation
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive user guide
- **[Quick Start](QUICKSTART.md)** - Get started in 5 minutes
- **[Configuration](docs/CONFIG.md)** - Configuration options
- **[Support](docs/SUPPORT.md)** - Troubleshooting and help

### Component Documentation
- **[Artifacts](docs/ARTIFACTS.md)** - Supported artifact types and parsing
- **[Cloud Forensics](docs/CLOUD.md)** - AWS, Azure, and GCP investigations
- **[AI Agent](docs/AI_AGENT.md)** - Natural language analysis
- **[SIEM Integration](docs/SIEM.md)** - Splunk and Elasticsearch

### Technical Documentation
- **[Tools](docs/TOOLS.md)** - Integrated forensic tools
- **[Update Guide](docs/UPDATE_GUIDE.md)** - Update procedures
- **[Contributing](docs/CONTRIBUTION.md)** - Contribution guidelines

---

## 💡 Example Workflows

### Incident Response

```bash
# 1. Quick triage acquisition
python3 acquisition/python/gandalf.py Password 192.168.1.100 -u admin -o /evidence

# 2. Rapid analysis
elrond -C -c IR-2024-001 -s /evidence -o /cases/IR-2024-001

# 3. Identify attack techniques
python3 -m rivendell.mitre.mapper /cases/IR-2024-001

# 4. Query for indicators
rivendell-ai query IR-2024-001 "What lateral movement occurred?"

# 5. Export to SIEM for correlation
python3 -m rivendell.siem.splunk_exporter \
  --case-id IR-2024-001 \
  --data-dir /cases/IR-2024-001 \
  --hec-url https://splunk:8088 \
  --hec-token TOKEN
```

### Malware Analysis

```bash
# 1. Acquire infected system
python3 acquisition/python/gandalf.py Password 192.168.1.50 -M -o /evidence

# 2. Analyze with focus on persistence
elrond -C -c MAL-001 -s /evidence -m /evidence/memory.dmp -o /output

# 3. Extract IOCs
rivendell-ai query MAL-001 "What IOCs were detected?"

# 4. Map to MITRE ATT&CK
python3 -m rivendell.mitre.mapper /output

# 5. Generate malware report
rivendell-ai summary MAL-001 --format markdown --output malware_report.md
```

### Cloud Investigation

```bash
# 1. Acquire cloud logs
python3 -m rivendell.cloud.cli aws acquire-logs --days 30 --output ./logs

# 2. Acquire VM snapshot
python3 -m rivendell.cloud.cli aws acquire-disk \
  --instance-id i-1234567890 \
  --output ./snapshots

# 3. Analyze logs
python3 -m rivendell.cloud.cli aws analyze-logs \
  --log-file ./logs/cloudtrail.json

# 4. Index and query
rivendell-ai index CLOUD-001 ./logs
rivendell-ai query CLOUD-001 "What suspicious AWS API calls were made?"
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTION.md](docs/CONTRIBUTION.md) for guidelines.

**Ways to Contribute:**
- Report bugs and request features
- Improve documentation
- Add support for new artifacts
- Develop integrations
- Share use cases and workflows

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Rivendell integrates many excellent open-source forensic tools:

- **Volatility 3** - Memory forensics framework
- **Plaso/log2timeline** - Timeline generation
- **RegRipper** - Registry analysis
- **Bulk Extractor** - IOC extraction
- **MITRE ATT&CK** - Adversary tactics and techniques
- **Ollama** - Local LLM inference
- **LangChain** - AI orchestration

And 25+ additional tools. See [TOOLS.md](docs/TOOLS.md) for the complete list.

---

## 📞 Support

- **Documentation**: See [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/rivendell/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rivendell/discussions)
- **Support Guide**: [SUPPORT.md](docs/SUPPORT.md)

---

## 🗺️ Roadmap

**v2.2 (Planned):**
- Mobile device forensics (iOS, Android)
- Network forensics integration
- Automated reporting enhancements
- Additional SIEM integrations

**v2.3 (Future):**
- Collaborative investigation features
- Advanced ML-based anomaly detection
- Container forensics (Docker, Kubernetes)
- Threat intelligence integration

---

## 📊 Project Stats

- **Lines of Code**: 50,000+
- **Integrated Tools**: 30+
- **Supported Platforms**: Windows, Linux, macOS
- **Cloud Providers**: AWS, Azure, GCP
- **MITRE ATT&CK Techniques**: 100+
- **Artifact Types**: 50+

---

**Built with ❤️ for the DFIR community**

[⬆ Back to Top](#rivendell-dfir-suite)

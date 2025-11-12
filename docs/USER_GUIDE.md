# Rivendell DFIR Suite - User Guide

**Version:** 2.1.0
**Last Updated:** 2025-11-12

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Components](#core-components)
4. [Quick Start](#quick-start)
5. [Feature Guides](#feature-guides)
6. [Configuration](#configuration)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

Rivendell is a comprehensive Digital Forensics and Incident Response (DFIR) suite that provides:

- **Remote Acquisition** (Gandalf) - Collect forensic artifacts from remote systems
- **Automated Analysis** (Elrond) - Process and analyze evidence
- **MITRE ATT&CK Integration** - Map findings to attack techniques
- **Cloud Forensics** - AWS, Azure, and GCP support
- **AI-Powered Analysis** - Natural language queries of investigation data
- **SIEM Integration** - Export to Splunk and Elasticsearch

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Rivendell Suite                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Gandalf    │  │    Elrond    │  │    AI     │ │
│  │ Acquisition  │→ │   Analysis   │→ │  Agent    │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │        MITRE ATT&CK Mapping Engine            │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │     Cloud Forensics (AWS/Azure/GCP)           │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │        SIEM Integration (Splunk/ELK)          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Installation

### Quick Installation

Choose your platform:

**Linux:**
```bash
git clone https://github.com/yourusername/rivendell.git
cd rivendell
chmod +x scripts/install_linux.sh
sudo ./scripts/install_linux.sh
```

**macOS:**
```bash
git clone https://github.com/yourusername/rivendell.git
cd rivendell
chmod +x scripts/install_macos.sh
./scripts/install_macos.sh
```

**Windows (WSL2):**
```powershell
git clone https://github.com/yourusername/rivendell.git
cd rivendell
.\scripts\install_windows_wsl.ps1
```

### Dependencies

**Core Requirements:**
- Python 3.8+
- Volatility 3 (memory analysis)
- Plaso/log2timeline (timeline generation)
- 30+ forensic tools (see [TOOL_COMPATIBILITY.md](TOOL_COMPATIBILITY.md))

**Optional:**
- Docker (for containerized deployment)
- Ollama (for AI agent)
- Splunk/Elasticsearch (for SIEM integration)

### Verification

```bash
elrond --check-dependencies
```

---

## Core Components

### 1. Gandalf - Remote Acquisition

Collect forensic artifacts from remote or local systems.

**Key Features:**
- Multi-platform (Windows, Linux, macOS)
- Remote acquisition via SSH/PowerShell
- Encrypted evidence collection
- Memory dump acquisition
- Audit logging with SHA256 hashing

**Basic Usage:**
```bash
# Local acquisition
sudo python3 acquisition/python/gandalf.py Password Local -M -o /evidence

# Remote acquisition (SSH)
python3 acquisition/python/gandalf.py Password 192.168.1.100 -u admin -M -o /evidence

# Windows remote (PowerShell)
.\acquisition\powershell\gandalf.ps1 -Target 192.168.1.100 -User admin -Memory -Output C:\evidence
```

See: [gandalf-README.md](gandalf-README.md)

### 2. Elrond - Automated Analysis

Process and analyze forensic evidence with automated tooling.

**Key Features:**
- Automated artifact parsing
- Timeline generation with Plaso
- Memory forensics with Volatility 3
- Registry analysis
- Event log parsing
- Browser artifact extraction
- IOC detection

**Basic Usage:**
```bash
# Process evidence (Collect mode)
elrond -C -c CASE-001 -s /evidence -o /output

# Analyze existing extraction (Gandalf mode)
elrond -G -c CASE-001 -s /extracted_data -o /output

# With memory analysis
elrond -C -c CASE-001 -s /evidence -m /memory.dmp -o /output
```

See: [elrond-README.md](elrond-README.md)

### 3. MITRE ATT&CK Integration

Automatically map forensic findings to MITRE ATT&CK techniques.

**Features:**
- Auto-updates from MITRE ATT&CK framework
- Technique mapping for artifacts
- ATT&CK matrix dashboard generation
- Coverage analysis

**Usage:**
```bash
# Update MITRE data
python3 -m rivendell.mitre.updater

# Map artifacts to techniques
python3 -m rivendell.mitre.mapper /path/to/artifacts

# Generate dashboard
python3 -m rivendell.mitre.dashboard -o /output
```

See: [FEATURE1_MITRE_INTEGRATION.md](FEATURE1_MITRE_INTEGRATION.md)

### 4. Cloud Forensics

Acquire and analyze cloud infrastructure across major providers.

**Supported Providers:**
- AWS (EC2, CloudTrail, S3)
- Azure (VMs, Activity Logs, Storage)
- GCP (Compute Engine, Cloud Logging, Storage)

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
  --log-file cloudtrail.json
```

See: [FEATURE4_CLOUD_FORENSICS.md](FEATURE4_CLOUD_FORENSICS.md)

### 5. AI-Powered Analysis Agent

Query investigation data using natural language.

**Features:**
- Natural language queries
- Investigation suggestions
- Case summaries
- Web chat interface
- Privacy-focused local LLM

**Usage:**
```bash
# Index case data
rivendell-ai index CASE-001 /output/CASE-001

# Query the case
rivendell-ai query CASE-001 "What PowerShell commands were executed?"

# Generate summary
rivendell-ai summary CASE-001 --format markdown

# Start web interface
python3 -m rivendell.ai.web_interface
# Visit http://localhost:5687/ai/chat/CASE-001
```

See: [FEATURE5_AI_AGENT.md](FEATURE5_AI_AGENT.md)

---

## Quick Start

### Complete Investigation Workflow

**Step 1: Acquire Evidence**
```bash
# From remote Windows system
python3 acquisition/python/gandalf.py Password 192.168.1.100 \
  -u administrator \
  -M \
  -o /evidence/CASE-001
```

**Step 2: Process Evidence**
```bash
# Analyze with Elrond
elrond -C \
  -c CASE-001 \
  -s /evidence/CASE-001 \
  -m /evidence/CASE-001/memory.dmp \
  -o /cases/CASE-001 \
  --veryverbose
```

**Step 3: MITRE Mapping**
```bash
# Map findings to ATT&CK
python3 -m rivendell.mitre.mapper /cases/CASE-001
```

**Step 4: Index for AI**
```bash
# Index artifacts for AI queries
rivendell-ai index CASE-001 /cases/CASE-001
```

**Step 5: Investigate**
```bash
# Query with AI
rivendell-ai query CASE-001 "What were the initial access vectors?"

# Generate report
rivendell-ai summary CASE-001 --format markdown --output report.md
```

**Step 6: Export to SIEM**
```bash
# Export to Splunk
python3 -m rivendell.siem.splunk_exporter \
  --case-id CASE-001 \
  --data-dir /cases/CASE-001 \
  --hec-url https://splunk:8088 \
  --hec-token YOUR_TOKEN
```

---

## Feature Guides

### Timeline Analysis

Generate comprehensive timelines using Plaso:

```bash
# Create timeline
elrond -C -c CASE-001 -s /evidence -t -o /output

# Timeline with date range
elrond -C -c CASE-001 -s /evidence -t \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  -o /output

# Query timeline with AI
rivendell-ai query CASE-001 "Show events between 14:00 and 15:00 on Jan 15"
```

### Memory Forensics

Analyze memory dumps with Volatility 3:

```bash
# Automatic profile detection
elrond -C -c CASE-001 -s /evidence -m /memory.dmp -o /output

# Specify profile
elrond -C -c CASE-001 -s /evidence \
  -m /memory.dmp \
  -p Win10x64_19041 \
  -o /output

# Query memory artifacts
rivendell-ai query CASE-001 "What processes were running in memory?"
```

### Cloud Investigations

#### AWS CloudTrail Analysis

```bash
# Acquire logs
python3 -m rivendell.cloud.cli aws acquire-logs \
  --days 7 \
  --analyze \
  --output ./logs

# Check for suspicious activities
rivendell-ai query CLOUD-CASE-001 \
  "What suspicious AWS API calls were made?"
```

#### Azure Incident Response

```bash
# List VMs
python3 -m rivendell.cloud.cli azure list \
  --credentials azure_creds.json

# Acquire VM disk snapshot
python3 -m rivendell.cloud.cli azure acquire-disk \
  --instance-id suspicious-vm \
  --resource-group production \
  --output ./output
```

### IOC Detection

Automatically extract indicators of compromise:

```bash
# Extract IOCs during analysis
elrond -C -c CASE-001 -s /evidence --extract-iocs -o /output

# Query IOCs
rivendell-ai query CASE-001 "List all malicious IP addresses detected"

# Export IOCs for sharing
python3 -m rivendell.tools.ioc_exporter \
  --case-id CASE-001 \
  --format stix \
  --output iocs.json
```

### Browser Forensics

Extract and analyze browser artifacts:

```bash
# Browser artifacts only
elrond -C -c CASE-001 -s /evidence --browser-only -o /output

# Query browser activity
rivendell-ai query CASE-001 \
  "What websites were visited before the incident?"
```

---

## Configuration

### Main Configuration

Edit `config/rivendell.yml`:

```yaml
# General settings
logging:
  level: INFO
  file: /var/log/rivendell.log

# Output settings
output:
  base_dir: /cases
  compress: true
  encryption: true

# Analysis settings
analysis:
  parallel_processing: true
  max_workers: 4
  memory_limit_gb: 16
```

### MITRE ATT&CK Configuration

Edit `config/mitre.yml`:

```yaml
mitre:
  auto_update: true
  update_interval_days: 7
  data_dir: /opt/rivendell/data/mitre
```

### Cloud Forensics Configuration

Edit `config/cloud.yml`:

```yaml
cloud_forensics:
  enabled: true

  aws:
    enabled: true
    regions:
      - us-east-1
      - us-west-2
```

### AI Agent Configuration

Edit `config/ai.yml`:

```yaml
ai_agent:
  enabled: true

  model:
    type: local
    ollama:
      model_name: "llama3"

  web_interface:
    enabled: true
    port: 5687
```

See: [CONFIG.md](CONFIG.md)

---

## Advanced Usage

### Parallel Processing

Process multiple cases simultaneously:

```bash
# Process multiple evidence sources
for evidence in /evidence/*; do
  caseid=$(basename "$evidence")
  elrond -C -c "$caseid" -s "$evidence" -o "/cases/$caseid" &
done
wait
```

### Custom Analysis Pipelines

Create custom analysis workflows:

```python
from rivendell.analysis import AnalysisPipeline
from rivendell.mitre import TechniqueMapper

# Create pipeline
pipeline = AnalysisPipeline("CASE-001")

# Add stages
pipeline.add_stage("extract_artifacts")
pipeline.add_stage("parse_registry")
pipeline.add_stage("analyze_memory")
pipeline.add_stage("generate_timeline")

# Run with custom options
results = pipeline.run(
    source="/evidence",
    output="/output",
    parallel=True,
    workers=8
)

# Map to MITRE
mapper = TechniqueMapper()
techniques = mapper.map_artifacts(results.artifacts)
```

### Integration with Other Tools

#### Export to CyberChef

```bash
# Extract and format for CyberChef
python3 -m rivendell.tools.cyberchef_export \
  --case-id CASE-001 \
  --artifact-type "encoded_strings" \
  --output recipe.json
```

#### MISP Integration

```bash
# Export IOCs to MISP
python3 -m rivendell.integrations.misp \
  --case-id CASE-001 \
  --misp-url https://misp.local \
  --misp-key YOUR_KEY \
  --create-event
```

### Automation

#### Scheduled Evidence Collection

```bash
# Cron job for daily collection
0 2 * * * /usr/local/bin/gandalf.py Password 192.168.1.100 -o /evidence/$(date +\%Y\%m\%d)
```

#### Automated Analysis

```bash
# Watch directory for new evidence
python3 -m rivendell.tools.auto_analyzer \
  --watch-dir /evidence \
  --output-dir /cases \
  --auto-index
```

---

## Troubleshooting

### Common Issues

#### "Tool not found" Errors

```bash
# Check dependencies
elrond --check-dependencies

# Install missing tools
elrond --install

# Manual installation
sudo apt-get install volatility3 plaso-tools
```

#### Memory Analysis Failures

```bash
# Check memory dump
file /path/to/memory.dmp

# Try different profile
elrond -C -c CASE-001 -m /memory.dmp -p Win10x64_19041

# Use Volatility directly
vol3 -f /memory.dmp windows.info
```

#### AI Agent Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Check vector database
rivendell-ai info CASE-001
```

#### SIEM Export Failures

```bash
# Test connection
curl -k https://splunk:8088/services/collector/health

# Verify HEC token
python3 -m rivendell.siem.splunk_test --hec-token YOUR_TOKEN
```

### Debug Mode

Enable verbose logging:

```bash
# Maximum verbosity
elrond -C -c CASE-001 -s /evidence --veryverbose

# Debug logs
export RIVENDELL_DEBUG=1
python3 -m rivendell.analysis.engine
```

### Getting Help

**Documentation:**
- [Quick Start Guide](QUICK_START.md)
- [Tool Compatibility](TOOL_COMPATIBILITY.md)
- [Configuration Guide](CONFIG.md)
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)

**Community:**
- GitHub Issues: https://github.com/yourusername/rivendell/issues
- Discussions: https://github.com/yourusername/rivendell/discussions

**Support:**
- See [SUPPORT.md](SUPPORT.md)
- See [CONTRIBUTION.md](CONTRIBUTION.md)

---

## Best Practices

### Evidence Handling

1. **Always verify hashes** - Check SHA256 hashes of acquired evidence
2. **Use encryption** - Enable encryption for sensitive evidence
3. **Maintain chain of custody** - Use audit logging throughout
4. **Document everything** - Keep detailed notes of all actions

### Analysis Workflow

1. **Start with triage** - Quick analysis to identify key artifacts
2. **Use timelines** - Timeline analysis helps identify attack patterns
3. **Map to MITRE** - Understand attacker techniques
4. **Leverage AI** - Use natural language queries for insights
5. **Export to SIEM** - Long-term storage and correlation

### Performance Optimization

1. **Use parallel processing** - Enable multi-threading
2. **Limit scope** - Use targeted artifact extraction when possible
3. **Optimize memory** - Set appropriate memory limits
4. **Use fast storage** - NVMe/SSD for working directory

---

## Appendix

### Supported Artifact Types

- **Windows**: Registry, Event Logs, Prefetch, MFT, USN Journal, Recycle Bin, LNK files, Jump Lists, SRUM
- **Linux**: System logs, shell history, cron jobs, user artifacts
- **macOS**: plists, unified logs, FSEvents, browser data
- **Memory**: Processes, network connections, loaded DLLs, registry hives
- **Cloud**: CloudTrail, Activity Logs, Cloud Logging, VM snapshots

### MITRE ATT&CK Coverage

Rivendell detects evidence for 100+ MITRE ATT&CK techniques across all tactics:

- Initial Access
- Execution
- Persistence
- Privilege Escalation
- Defense Evasion
- Credential Access
- Discovery
- Lateral Movement
- Collection
- Exfiltration
- Impact

See: [FEATURE2_COVERAGE_ANALYSIS.md](FEATURE2_COVERAGE_ANALYSIS.md)

---

**Version:** 2.1.0
**License:** See LICENSE
**Authors:** Rivendell DFIR Suite Contributors

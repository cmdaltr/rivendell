# Rivendell CLI Reference

**Version:** 2.1.0
**Command:** `elrond` (Analysis) | `gandalf` (Acquisition)

---

## Table of Contents

1. [Overview](#overview)
2. [Gandalf - Acquisition](#gandalf---acquisition)
3. [Elrond - Analysis](#elrond---analysis)
4. [MITRE ATT&CK Tools](#mitre-attck-tools)
5. [Cloud Forensics](#cloud-forensics)
6. [AI Agent](#ai-agent)
7. [SIEM Integration](#siem-integration)
8. [Utility Commands](#utility-commands)
9. [Configuration](#configuration)
10. [Common Workflows](#common-workflows)

---

## Overview

Rivendell provides command-line tools for forensic acquisition and analysis:

- **Gandalf** - Remote and local evidence acquisition
- **Elrond** - Automated forensic analysis and artifact processing
- **MITRE tools** - ATT&CK technique mapping and coverage analysis
- **Cloud tools** - AWS/Azure/GCP forensics
- **AI tools** - Natural language investigation queries
- **SIEM tools** - Export to Splunk/Elasticsearch

---

## Gandalf - Acquisition

### Overview

Gandalf acquires forensic artifacts from local or remote systems with encryption, audit logging, and chain of custody.

### Installation Locations

- **Python**: `acquisition/python/gandalf.py`
- **Bash**: `acquisition/bash/gandalf.sh`
- **PowerShell**: `acquisition\powershell\Gandalf.ps1`

---

### Python Syntax

```bash
python3 acquisition/python/gandalf.py [ENCRYPTION] [TARGET] [OPTIONS]
```

**Parameters:**
- `ENCRYPTION`: Encryption password or `None` for no encryption
- `TARGET`: `Local` or IP address/hostname for remote acquisition

**Options:**
```
-u, --user USERNAME          Remote username (required for remote)
-M, --memory                 Include memory dump
-o, --output PATH            Output directory (default: /evidence)
--vss                        Include Volume Shadow Copies (Windows)
--Userprofiles              Collect user profiles
--encrypt                    Encrypt evidence archive
-h, --help                   Show help message
```

---

### Examples

#### Local Acquisition

```bash
# Basic local acquisition with encryption
sudo python3 acquisition/python/gandalf.py Password Local -o /evidence/CASE-001

# With memory dump
sudo python3 acquisition/python/gandalf.py Password Local -M -o /evidence/CASE-001

# Comprehensive local acquisition
sudo python3 acquisition/python/gandalf.py SecurePass123 Local \
  -M \
  --vss \
  --Userprofiles \
  --encrypt \
  -o /evidence/COMPREHENSIVE-001
```

#### Remote Acquisition (Linux/macOS)

```bash
# Basic remote acquisition
python3 acquisition/python/gandalf.py Password 192.168.1.100 \
  -u administrator \
  -o /evidence/REMOTE-001

# With memory and VSS
python3 acquisition/python/gandalf.py Password 192.168.1.100 \
  -u admin \
  -M \
  --vss \
  -o /evidence/REMOTE-001

# From multiple hosts
cat > hosts.list <<EOF
192.168.1.100
192.168.1.101
192.168.1.102
EOF

for host in $(cat hosts.list); do
  python3 acquisition/python/gandalf.py Password "$host" \
    -u admin \
    -M \
    -o "/evidence/HOST-$host"
done
```

#### Remote Acquisition (Windows)

```powershell
# Local acquisition
.\acquisition\powershell\Gandalf.ps1 `
  -Local `
  -Password "Password123" `
  -OutputDir "C:\Evidence\LOCAL-001"

# Remote acquisition
.\acquisition\powershell\Gandalf.ps1 `
  -Target "192.168.1.100" `
  -Username "Administrator" `
  -Password "Password123" `
  -IncludeMemory `
  -IncludeVSS `
  -OutputDir "C:\Evidence\REMOTE-001"

# Multiple hosts
$hosts = @("192.168.1.100", "192.168.1.101", "192.168.1.102")
foreach ($host in $hosts) {
    .\acquisition\powershell\Gandalf.ps1 `
      -Target $host `
      -Username "admin" `
      -Password "Password123" `
      -IncludeMemory `
      -OutputDir "C:\Evidence\HOST-$host"
}
```

---

### Bash Syntax

```bash
./acquisition/bash/gandalf.sh [TARGET] [USERNAME] [PASSWORD] [OUTPUT] [OPTIONS]
```

**Example:**
```bash
sudo ./acquisition/bash/gandalf.sh 192.168.1.100 admin Password /evidence/CASE-001 --memory
```

---

### Output Structure

Gandalf creates a tarball with the following structure:

```
hostname.tar.gz
├── artefacts/
│   ├── host.info              # System information
│   ├── memory/                # Memory dump (if -M used)
│   │   └── hostname.mem
│   ├── logs/                  # System logs
│   ├── registry/              # Windows registry (Windows only)
│   ├── browsers/              # Browser artifacts
│   ├── users/                 # User profiles (if --Userprofiles)
│   └── vss/                   # Volume shadow copies (if --vss)
├── log.audit                  # Audit log with SHA256 hashes
└── log.meta                   # Acquisition metadata
```

---

### Security Features

1. **Encryption**: AES-256 encryption using provided password
2. **Hashing**: SHA256 hashes for all acquired files in `log.audit`
3. **Chain of Custody**: Detailed metadata in `log.meta`
4. **Audit Trail**: All operations logged with timestamps
5. **Read-Only**: Evidence acquired without modification

---

## Elrond - Analysis

### Overview

Elrond automates forensic analysis of acquired evidence, processing artifacts through multiple analysis phases.

### Syntax

```bash
elrond [FLAGS] CASE_ID SOURCE_PATH OUTPUT_PATH [OPTIONS]
```

**Required Arguments:**
- `CASE_ID`: Case identifier (e.g., CASE-2025-001)
- `SOURCE_PATH`: Path to evidence (disk image, Gandalf archive, or directory)
- `OUTPUT_PATH`: Output directory for results

---

### Analysis Modes

**Collection Mode** (`-C, --Collect`)
- Mount disk images
- Extract artifacts from filesystems
- Parse MFT, USN Journal, event logs
- Collect browser artifacts, registry, etc.

**Processing Mode** (`-P, --Process`)
- Parse collected artifacts
- Convert binary data to CSV/JSON
- Generate structured reports

**Analysis Mode** (`-A, --Analysis`)
- Timeline generation
- IOC extraction
- Pattern matching
- YARA scanning
- Keyword search

---

### Common Flags

**Phase Flags:**
```
-C, --Collect               Collection phase
-P, --Process               Processing phase
-A, --Analysis              Analysis phase
-M, --Memory                Memory analysis with Volatility3
-T, --Timeline              Generate timeline with Plaso
```

**Feature Flags:**
```
-I, --extractIocs           Extract indicators of compromise
-Y, --Yara PATH             Scan with YARA rules
-K, --Keywords FILE         Search for keywords
-c, --vss                   Process Volume Shadow Copies
-U, --Userprofiles          Collect user profiles
```

**Speed Modes:**
```
-q, --quick                 Quick analysis (essential artifacts only)
-Q, --superQuick            Super quick (critical artifacts only)
-B, --Brisk                 Brisk mode (balanced speed/thoroughness)
-X, --eXhaustive            Exhaustive analysis (all artifacts)
```

**SIEM Export:**
```
-S, --Splunk                Export to Splunk HEC
-E, --Elastic               Export to Elasticsearch
-N, --Navigator             Generate MITRE Navigator layer
```

**Other:**
```
--veryverbose               Maximum verbosity
-h, --help                  Show help
--version                   Show version
--check-dependencies        Verify tool installation
```

---

### Examples

#### Basic Analysis

```bash
# Collect and process disk image
elrond -C -P CASE-001 /evidence/disk.E01 /output/CASE-001

# Full workflow
elrond -C -P -A CASE-001 /evidence/disk.E01 /output/CASE-001

# With memory analysis
elrond -C -P -A -M CASE-001 \
  /evidence/disk.E01 \
  /output/CASE-001 \
  -m /evidence/memory.dmp

# Timeline generation
elrond -C -P -T CASE-001 /evidence/disk.E01 /output/CASE-001
```

#### Speed Modes

```bash
# Quick triage
elrond -C -P -A -q CASE-001 /evidence/disk.E01 /output/CASE-001

# Brisk mode (recommended for most cases)
elrond -C -P -A -B CASE-001 /evidence/disk.E01 /output/CASE-001

# Exhaustive analysis
elrond -C -P -A -X CASE-001 /evidence/disk.E01 /output/CASE-001
```

#### Advanced Features

```bash
# IOC extraction and YARA scanning
elrond -C -P -A -I \
  -Y /path/to/yara/rules \
  CASE-001 /evidence/disk.E01 /output/CASE-001

# Keyword search
elrond -C -P -A -K /path/to/keywords.txt \
  CASE-001 /evidence/disk.E01 /output/CASE-001

# VSS processing
elrond -C -P -A -c CASE-001 /evidence/disk.E01 /output/CASE-001

# User profile collection
elrond -C -P -A -U CASE-001 /evidence/disk.E01 /output/CASE-001
```

#### SIEM Integration

```bash
# Export to Splunk
elrond -C -P -A -S CASE-001 /evidence/disk.E01 /output/CASE-001

# Export to Elasticsearch
elrond -C -P -A -E CASE-001 /evidence/disk.E01 /output/CASE-001

# Both SIEM platforms
elrond -C -P -A -S -E CASE-001 /evidence/disk.E01 /output/CASE-001

# With MITRE Navigator
elrond -C -P -A -S -N CASE-001 /evidence/disk.E01 /output/CASE-001
```

#### Complete Workflow

```bash
# Comprehensive analysis with all features
elrond -C -P -A -M -T -I -c -U -B -N -S \
  CASE-001 \
  /evidence/disk.E01 \
  /output/CASE-001 \
  -m /evidence/memory.dmp \
  -Y /opt/yara-rules \
  -K /opt/keywords.txt \
  --veryverbose
```

---

### Output Structure

Elrond creates structured output:

```
/output/CASE-001/
├── collected/                 # Collected artifacts
│   ├── registry/
│   ├── event_logs/
│   ├── prefetch/
│   └── browsers/
├── processed/                 # Parsed data
│   ├── timeline.csv          # Master timeline
│   ├── registry.csv          # Registry analysis
│   ├── browsers.csv          # Browser history
│   ├── event_logs.csv        # Parsed event logs
│   └── file_system.csv       # MFT analysis
├── analysis/                  # Analysis results
│   ├── iocs.csv              # Indicators of Compromise
│   ├── keywords.csv          # Keyword matches
│   ├── yara_matches.csv      # YARA rule matches
│   └── attck_matrix.json     # MITRE ATT&CK mapping
├── memory/                    # Memory analysis (if -M)
│   ├── processes.csv
│   ├── network.csv
│   ├── registry.csv
│   └── filescan.csv
├── splunk/                    # Splunk export (if -S)
│   └── events.json
├── elastic/                   # Elastic export (if -E)
│   └── events.json
├── navigator/                 # MITRE Navigator (if -N)
│   └── attck_layer.json
└── logs/
    ├── elrond.log            # Execution log
    └── errors.log            # Error log
```

---

## MITRE ATT&CK Tools

### Update MITRE Data

Download latest MITRE ATT&CK framework data:

```bash
# Update framework data
python3 -m rivendell.mitre.updater

# Force update (ignore cache)
python3 -m rivendell.mitre.updater --force

# Specify ATT&CK version
python3 -m rivendell.mitre.updater --version 14.1
```

---

### Map Artifacts to Techniques

Automatically map forensic artifacts to ATT&CK techniques:

```bash
# Map case artifacts
python3 -m rivendell.mitre.mapper /output/CASE-001

# Specify output location
python3 -m rivendell.mitre.mapper /output/CASE-001 -o /output/CASE-001/attck.json

# Verbose output
python3 -m rivendell.mitre.mapper /output/CASE-001 --verbose
```

**Output:** JSON file with technique mappings

---

### Generate ATT&CK Dashboard

Create HTML dashboard of detected techniques:

```bash
# Generate dashboard
python3 -m rivendell.mitre.dashboard -o /output/dashboard.html

# For specific case
python3 -m rivendell.mitre.dashboard \
  --case-data /output/CASE-001/attck.json \
  -o /output/CASE-001/dashboard.html

# Include coverage statistics
python3 -m rivendell.mitre.dashboard \
  --show-coverage \
  -o /output/dashboard.html
```

---

### Generate Navigator Layer

Create ATT&CK Navigator layer file:

```bash
# Generate layer
python3 -m rivendell.mitre.navigator /output/CASE-001 -o navigator.json

# With custom name
python3 -m rivendell.mitre.navigator /output/CASE-001 \
  --name "CASE-001 Analysis" \
  --description "Investigation findings" \
  -o navigator.json
```

Upload `navigator.json` to https://mitre-attack.github.io/attack-navigator/

---

### Coverage Analysis

Analyze detection coverage across ATT&CK matrix:

```bash
# Analyze coverage for case
python3 -m rivendell.coverage.analyzer /output/CASE-001

# Real-time monitoring
python3 -m rivendell.coverage.monitor --watch /output

# Generate coverage report
python3 -m rivendell.coverage.dashboard -o coverage.html
```

---

## Cloud Forensics

### AWS Commands

#### List Resources

```bash
# List EC2 instances
python3 -m rivendell.cloud.cli aws list --credentials aws_creds.json

# List instances in specific region
python3 -m rivendell.cloud.cli aws list \
  --credentials aws_creds.json \
  --region us-east-1

# Filter by tags
python3 -m rivendell.cloud.cli aws list \
  --credentials aws_creds.json \
  --tags "Environment=Production"
```

#### Acquire Disk Snapshot

```bash
# Acquire EC2 disk
python3 -m rivendell.cloud.cli aws acquire-disk \
  --instance-id i-1234567890abcdef0 \
  --output ./snapshots/AWS-001

# Specific volume
python3 -m rivendell.cloud.cli aws acquire-disk \
  --instance-id i-1234567890abcdef0 \
  --volume-id vol-1234567890abcdef0 \
  --output ./snapshots/AWS-001

# With credentials file
python3 -m rivendell.cloud.cli aws acquire-disk \
  --credentials aws_creds.json \
  --instance-id i-1234567890abcdef0 \
  --output ./snapshots/AWS-001
```

#### Acquire CloudTrail Logs

```bash
# Last 7 days
python3 -m rivendell.cloud.cli aws acquire-logs \
  --days 7 \
  --output ./logs/AWS-001

# Specific services
python3 -m rivendell.cloud.cli aws acquire-logs \
  --days 30 \
  --services cloudtrail,vpc,s3 \
  --output ./logs/AWS-001

# Date range
python3 -m rivendell.cloud.cli aws acquire-logs \
  --start-date 2025-01-01 \
  --end-date 2025-01-15 \
  --output ./logs/AWS-001
```

#### Analyze CloudTrail

```bash
# Analyze logs
python3 -m rivendell.cloud.cli aws analyze-logs \
  --log-file ./logs/AWS-001/cloudtrail.json \
  --output ./analysis/AWS-001

# Filter by user
python3 -m rivendell.cloud.cli aws analyze-logs \
  --log-file ./logs/AWS-001/cloudtrail.json \
  --user suspicious-user \
  --output ./analysis/AWS-001

# Detect suspicious activity
python3 -m rivendell.cloud.cli aws analyze-logs \
  --log-file ./logs/AWS-001/cloudtrail.json \
  --detect-suspicious \
  --output ./analysis/AWS-001
```

---

### Azure Commands

#### List Resources

```bash
# List VMs
python3 -m rivendell.cloud.cli azure list --credentials azure_creds.json

# Specific resource group
python3 -m rivendell.cloud.cli azure list \
  --credentials azure_creds.json \
  --resource-group production
```

#### Acquire VM Disk

```bash
# Acquire disk snapshot
python3 -m rivendell.cloud.cli azure acquire-disk \
  --instance-id myvm \
  --resource-group mygroup \
  --output ./snapshots/AZURE-001

# With credentials
python3 -m rivendell.cloud.cli azure acquire-disk \
  --credentials azure_creds.json \
  --instance-id myvm \
  --resource-group mygroup \
  --output ./snapshots/AZURE-001
```

#### Acquire Activity Logs

```bash
# Last 30 days
python3 -m rivendell.cloud.cli azure acquire-logs \
  --days 30 \
  --output ./logs/AZURE-001

# Specific subscription
python3 -m rivendell.cloud.cli azure acquire-logs \
  --subscription-id abc-123 \
  --days 30 \
  --output ./logs/AZURE-001
```

---

### GCP Commands

#### List Resources

```bash
# List instances
python3 -m rivendell.cloud.cli gcp list --credentials gcp_creds.json

# Specific project
python3 -m rivendell.cloud.cli gcp list \
  --credentials gcp_creds.json \
  --project myproject
```

#### Acquire Disk Snapshot

```bash
# Acquire disk
python3 -m rivendell.cloud.cli gcp acquire-disk \
  --instance-id myinstance \
  --zone us-central1-a \
  --output ./snapshots/GCP-001

# With credentials
python3 -m rivendell.cloud.cli gcp acquire-disk \
  --credentials gcp_creds.json \
  --instance-id myinstance \
  --zone us-central1-a \
  --output ./snapshots/GCP-001
```

#### Acquire Cloud Logging

```bash
# Last 30 days
python3 -m rivendell.cloud.cli gcp acquire-logs \
  --days 30 \
  --output ./logs/GCP-001

# Filter by resource
python3 -m rivendell.cloud.cli gcp acquire-logs \
  --days 30 \
  --resource-type gce_instance \
  --output ./logs/GCP-001
```

---

## AI Agent

The AI agent enables natural language querying of investigation data.

### Index Case Data

Index artifacts for AI querying:

```bash
# Index case
rivendell-ai index CASE-001 /output/CASE-001

# Re-index (update)
rivendell-ai index CASE-001 /output/CASE-001 --reindex

# Verbose indexing
rivendell-ai index CASE-001 /output/CASE-001 --verbose
```

---

### Query Case

Ask natural language questions:

```bash
# Simple query
rivendell-ai query CASE-001 "What PowerShell commands were executed?"

# Complex query
rivendell-ai query CASE-001 "Show network connections to external IPs between 14:00 and 15:00"

# Multiple queries
rivendell-ai query CASE-001 "What MITRE techniques were detected?" \
  "Show lateral movement evidence" \
  "List persistence mechanisms"

# Save results
rivendell-ai query CASE-001 "What malware was detected?" -o results.txt
```

---

### Get Investigation Suggestions

Get AI-generated investigation suggestions:

```bash
# Get suggestions
rivendell-ai suggest CASE-001

# Detailed suggestions
rivendell-ai suggest CASE-001 --detailed

# Focus area
rivendell-ai suggest CASE-001 --focus "lateral movement"
```

---

### Generate Summary

Create investigation summaries:

```bash
# Markdown summary
rivendell-ai summary CASE-001 --format markdown --output summary.md

# HTML report
rivendell-ai summary CASE-001 --format html --output report.html

# JSON export
rivendell-ai summary CASE-001 --format json --output report.json

# Email-friendly text
rivendell-ai summary CASE-001 --format text --output summary.txt
```

---

### Web Interface

Start web chat interface:

```bash
# Start server
python3 -m rivendell.ai.web_interface

# Custom port
python3 -m rivendell.ai.web_interface --port 8080

# Access at http://localhost:5687/ai/chat/CASE-001
```

---

### Case Management

```bash
# List indexed cases
rivendell-ai list

# Show case info
rivendell-ai info CASE-001

# Delete case index
rivendell-ai delete CASE-001

# Export case data
rivendell-ai export CASE-001 -o case_export.json
```

---

## SIEM Integration

### Splunk Export

Export data to Splunk via HTTP Event Collector (HEC):

```bash
# Export case
python3 -m rivendell.siem.splunk_exporter \
  --case-id CASE-001 \
  --data-dir /output/CASE-001 \
  --hec-url https://splunk.company.com:8088 \
  --hec-token YOUR_HEC_TOKEN

# Specific source type
python3 -m rivendell.siem.splunk_exporter \
  --case-id CASE-001 \
  --data-dir /output/CASE-001 \
  --hec-url https://splunk:8088 \
  --hec-token YOUR_TOKEN \
  --source-type rivendell:forensics

# Test connection
python3 -m rivendell.siem.splunk_test \
  --hec-url https://splunk:8088 \
  --hec-token YOUR_TOKEN
```

---

### Elasticsearch Export

Export data to Elasticsearch:

```bash
# Export case
python3 -m rivendell.siem.elastic_exporter \
  --case-id CASE-001 \
  --data-dir /output/CASE-001 \
  --elastic-url https://elastic:9200 \
  --index rivendell-case-001

# With authentication
python3 -m rivendell.siem.elastic_exporter \
  --case-id CASE-001 \
  --data-dir /output/CASE-001 \
  --elastic-url https://elastic:9200 \
  --username elastic \
  --password YOUR_PASSWORD \
  --index rivendell-case-001

# Test connection
python3 -m rivendell.siem.elastic_test \
  --elastic-url https://elastic:9200 \
  --username elastic \
  --password YOUR_PASSWORD
```

---

## Utility Commands

### Check Dependencies

Verify installed forensic tools:

```bash
# Check all dependencies
elrond --check-dependencies

# Show versions
elrond --check-dependencies --verbose

# Check specific tools
python3 -m rivendell.utils.check_tools volatility plaso sleuthkit
```

---

### Version Information

```bash
# Show version
elrond --version

# Detailed version info
python3 -m rivendell.utils.version --detailed

# Check for updates
python3 -m rivendell.utils.version --check-updates
```

---

### Logging

```bash
# View logs
tail -f /var/log/rivendell/elrond.log

# Search logs
grep ERROR /var/log/rivendell/elrond.log

# Clear logs
python3 -m rivendell.utils.clear_logs
```

---

### Database Management

```bash
# Initialize database
python3 -m rivendell.db.init

# Run migrations
python3 -m rivendell.db.migrate

# Backup database
python3 -m rivendell.db.backup -o /backups/rivendell-$(date +%Y%m%d).sql

# Restore database
python3 -m rivendell.db.restore /backups/rivendell-20250115.sql
```

---

## Configuration

### Environment Variables

```bash
# Set Rivendell base directory
export RIVENDELL_HOME=/opt/rivendell

# Set output directory
export RIVENDELL_OUTPUT=/cases

# Set log level
export RIVENDELL_LOG_LEVEL=DEBUG

# Enable debug mode
export RIVENDELL_DEBUG=1

# SIEM configuration
export SPLUNK_HEC_URL=https://splunk:8088
export SPLUNK_HEC_TOKEN=your_token_here
export ELASTIC_URL=https://elastic:9200
export ELASTIC_USERNAME=elastic
export ELASTIC_PASSWORD=your_password
```

---

### Configuration Files

**Main Config:** `/etc/rivendell/config.yml`

```yaml
general:
  log_level: INFO
  output_dir: /cases
  temp_dir: /tmp/rivendell

analysis:
  parallel_processing: true
  max_workers: 4
  memory_limit_gb: 16

mitre:
  auto_update: true
  update_interval_days: 7

siem:
  splunk:
    enabled: true
    hec_url: https://splunk:8088
    hec_token: YOUR_TOKEN
  elastic:
    enabled: true
    url: https://elastic:9200
    username: elastic
    password: YOUR_PASSWORD
```

---

## Common Workflows

### 1. Complete Investigation

```bash
# Step 1: Acquire evidence
python3 acquisition/python/gandalf.py Password 192.168.1.100 \
  -u admin -M -o /evidence/CASE-001

# Step 2: Analyze evidence
elrond -C -P -A -M -T -B CASE-001 \
  /evidence/CASE-001/*.tar.gz \
  /output/CASE-001 \
  -m /evidence/CASE-001/memory.dmp

# Step 3: Map to MITRE
python3 -m rivendell.mitre.mapper /output/CASE-001

# Step 4: Index for AI
rivendell-ai index CASE-001 /output/CASE-001

# Step 5: Query investigation
rivendell-ai query CASE-001 "What was the initial access vector?"

# Step 6: Export to SIEM
python3 -m rivendell.siem.splunk_exporter \
  --case-id CASE-001 \
  --data-dir /output/CASE-001 \
  --hec-url https://splunk:8088 \
  --hec-token YOUR_TOKEN

# Step 7: Generate report
rivendell-ai summary CASE-001 --format markdown -o report.md
```

---

### 2. Quick Triage

```bash
# Fast analysis for initial triage
python3 acquisition/python/gandalf.py None Local -o /evidence/TRIAGE-001
elrond -C -P -A -q TRIAGE-001 /evidence/TRIAGE-001 /output/TRIAGE-001
rivendell-ai query TRIAGE-001 "What IOCs were detected?"
```

---

### 3. Cloud Investigation

```bash
# Acquire cloud logs
python3 -m rivendell.cloud.cli aws acquire-logs --days 7 --output ./logs/AWS-001

# Analyze cloud activity
python3 -m rivendell.cloud.cli aws analyze-logs \
  --log-file ./logs/AWS-001/cloudtrail.json \
  --detect-suspicious

# Query findings
rivendell-ai index AWS-001 ./logs/AWS-001
rivendell-ai query AWS-001 "What suspicious AWS API calls were made?"
```

---

### 4. Batch Processing

```bash
# Process multiple evidence files
for evidence in /evidence/*.tar.gz; do
  caseid=$(basename "$evidence" .tar.gz)
  elrond -C -P -A -B "$caseid" "$evidence" "/output/$caseid" &
done
wait

# Index all cases
for case in /output/*; do
  caseid=$(basename "$case")
  rivendell-ai index "$caseid" "$case"
done
```

---

## Troubleshooting

### Common Issues

**Tool not found errors:**
```bash
# Check what's missing
elrond --check-dependencies

# Install missing tools (Ubuntu/Debian)
sudo apt-get install volatility3 plaso-tools sleuthkit

# Install via pip
pip3 install volatility3
```

**Memory analysis failures:**
```bash
# Check dump file
file /path/to/memory.dmp

# Try different profile
vol3 -f /path/to/memory.dmp windows.info

# Use auto-detect
elrond -C -P -A -M CASE-001 /evidence /output -m /memory.dmp
```

**Permission errors:**
```bash
# Ensure proper permissions
sudo chown -R $USER:$USER /output
sudo chmod -R 755 /output

# Run with elevated privileges (for mounting)
sudo elrond -C CASE-001 /evidence/disk.E01 /output
```

**AI agent issues:**
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Rebuild index
rivendell-ai index CASE-001 /output/CASE-001 --reindex
```

---

## Getting Help

**Built-in Help:**
```bash
elrond --help
gandalf.py --help
rivendell-ai --help
```

**Documentation:**
- [API Reference](API.md)
- [User Guide](USER_GUIDE.md)
- [Quick Start](QUICKSTART.md)
- [Security Guide](SECURITY.md)

**Community:**
- GitHub Issues: https://github.com/cmdaltr/rivendell/issues
- Discussions: https://github.com/cmdaltr/rivendell/discussions

---

**Version:** 2.1.0
**Last Updated:** 2025-01-15
**License:** See LICENSE file

# Rivendell Quick Start Guide

Get up and running with Rivendell DF Acceleration Suite in minutes!

## 🚀 Quick Start (Docker - Recommended)

```bash
# Clone the repository
git clone https://github.com/cmdaltr/rivendell.git
cd rivendell

# Start all services
docker-compose up -d

# Access web interface
open http://localhost:8000

# Access API documentation
open http://localhost:8000/docs

# Check status
docker-compose ps

# View logs
docker-compose logs -f rivendell
```

**That's it!** The web interface is now available at http://localhost:8000

## 🔧 Quick Start (Local Installation)

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/cmdaltr/rivendell.git
cd rivendell

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install base dependencies
pip install -e .

# Install with web interface
pip install -e ".[web]"

# Install with SIEM support
pip install -e ".[web]" -r requirements/siem.txt
```

### 2. Start Web Interface

```bash
# Option 1: Using uvicorn directly
python3 -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using CLI
python3 cli/rivendell.py web --port 8000 --reload

# Access at http://localhost:8000
```

## 📥 Acquire Evidence

### Local Acquisition (Linux/macOS)

```bash
# Basic acquisition with password encryption
sudo python3 acquisition/python/gandalf.py Password Local -o /evidence

# With memory dump
sudo python3 acquisition/python/gandalf.py Password Local -M -o /evidence

# Using bash version
sudo bash acquisition/bash/gandalf.sh Password Local -m -o /evidence
```

### Remote Acquisition

```bash
# From single host
sudo python3 acquisition/python/gandalf.py Password Remote -h 192.168.1.100 -u analyst -M

# From multiple hosts (using hosts.list)
echo "192.168.1.100" > acquisition/lists/hosts.list
echo "192.168.1.101" >> acquisition/lists/hosts.list
sudo python3 acquisition/python/gandalf.py Password Remote -f acquisition/lists/hosts.list -M
```

### Windows Acquisition

```powershell
# Open PowerShell as Administrator
cd acquisition\windows

# Local acquisition
.\Invoke-Gandalf.ps1 Password Local -Memory

# Remote acquisition
.\Invoke-Gandalf.ps1 Password HOSTNAME -Memory -OutputDirectory D:\evidence
```

## 📁 Analysis Files (Keywords, YARA & IOC Watchlists)

To use keyword searching, YARA signature scanning, and IOC watchlist matching, place your files in the `files/` directory:

```
files/
├── keywords.txt           # One keyword per line
├── iocs.txt               # IOC watchlist (IPs, domains, hashes)
└── yara_rules/            # YARA rule files
    ├── malware.yar
    ├── suspicious.yara
    └── custom_rules.yar
```

This directory is automatically mounted into the Docker container at `/tmp/rivendell/files/`.

**Keywords File Format** (`keywords.txt`):
```
password
secret
api_key
credentials
```

**IOC Watchlist Format** (`iocs.txt`):
```
# Known malicious IPs
192.168.1.100
10.0.0.50

# Malicious domains
evil-domain.com
malware-c2.net

# File hashes (MD5, SHA1, SHA256)
d41d8cd98f00b204e9800998ecf8427e
```

**YARA Rules**: Place `.yar` or `.yara` files in the `yara_rules/` subdirectory.

When creating analysis jobs, reference these paths:
- Keywords: `/tmp/rivendell/files/keywords.txt`
- YARA: `/tmp/rivendell/files/yara_rules/`
- IOCs: `/tmp/rivendell/files/iocs.txt`

## 🔍 Analyze Evidence

### Quick Analysis

```bash
# Brisk mode (quick analysis with common settings)
python3 analysis/elrond.py CASE-001 /evidence/hostname.tar.gz /output -B

# Full analysis with all phases
python3 analysis/elrond.py CASE-001 /evidence/hostname.tar.gz /output -CPA
```

### With SIEM Export

```bash
# Export to Splunk
python3 analysis/elrond.py CASE-001 /evidence /output -CPAS

# Export to Elasticsearch
python3 analysis/elrond.py CASE-001 /evidence /output -CPAE

# Both
python3 analysis/elrond.py CASE-001 /evidence /output -CPASE
```

### Memory Analysis

```bash
# Analyze memory dump
python3 analysis/elrond.py MEM-001 /evidence/memory.mem /output -MP
```

## 🌐 Using the Web Interface

### Starting Jobs via API

```bash
# Create acquisition job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "CASE-001",
    "job_type": "acquisition",
    "target": "local",
    "options": {
      "encryption": "Password",
      "memory": true
    }
  }'

# Create analysis job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "CASE-001",
    "job_type": "analysis",
    "evidence_path": "/evidence/hostname.tar.gz",
    "output_path": "/output",
    "options": {
      "collect": true,
      "process": true,
      "analyze": true,
      "splunk": true
    }
  }'

# Check job status
curl http://localhost:8000/api/jobs/JOB-ID

# List all jobs
curl http://localhost:8000/api/jobs
```

### Using the Web UI

1. Open browser to `http://localhost:8000`
2. Click **"New Analysis"**
3. Fill in case details:
   - Case ID: `CASE-001`
   - Evidence Path: `/evidence/hostname.tar.gz`
   - Output Directory: `/output`
4. Select analysis options:
   - ✅ Collection
   - ✅ Processing
   - ✅ Analysis
   - ✅ Splunk Export
5. Click **"Start Analysis"**
6. Monitor progress in **"Job List"**
7. View results in **"Job Details"**

## 🔐 SIEM Setup (5-Minute Guide)

### Splunk Setup

1. **Install Splunk Enterprise 9.x**:
```bash
wget https://download.splunk.com/products/splunk/releases/9.1.2/linux/splunk-9.1.2-b6436b649711-Linux-x86_64.tgz
tar xvzf splunk*.tgz -C /opt
/opt/splunk/bin/splunk start --accept-license
```

2. **Enable HEC and create token**:
```bash
/opt/splunk/bin/splunk http-event-collector enable -auth admin:changeme
/opt/splunk/bin/splunk http-event-collector create rivendell-token -auth admin:changeme
```

3. **Configure Rivendell** (edit `.env`):
```bash
SPLUNK_ENABLED=true
SPLUNK_HOST=localhost
SPLUNK_PORT=8088
SPLUNK_HEC_TOKEN=your-token-here
```

### Elasticsearch Setup

1. **Install Elasticsearch 8.x**:
```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update && sudo apt-get install elasticsearch
sudo systemctl start elasticsearch
```

2. **Get credentials** (displayed on first start):
```bash
# Or reset password
/usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

3. **Configure Rivendell** (edit `.env`):
```bash
ELASTIC_ENABLED=true
ELASTIC_HOST=localhost
ELASTIC_PORT=9200
ELASTIC_SCHEME=https
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=your-password
ELASTIC_SSL_VERIFY=false  # Or provide CA cert
```

## 📊 Common Workflows

### Workflow 1: Quick Triage

```bash
# 1. Acquire from suspect system
sudo python3 acquisition/python/gandalf.py None Local -o /evidence

# 2. Quick analysis (Brisk mode)
python3 analysis/elrond.py TRIAGE-001 /evidence/*.tar.gz /output -B

# 3. Review IOCs
cat /output/TRIAGE-001/analysis/iocs.csv
```

### Workflow 2: Full Investigation with SIEM

```bash
# 1. Acquire from remote host with memory
sudo python3 acquisition/python/gandalf.py Password Remote -h 192.168.1.100 -u analyst -M

# 2. Full analysis with Splunk export
python3 analysis/elrond.py CASE-001 /evidence/*.tar.gz /output -CPAS

# 3. View in Splunk
# Navigate to: http://splunk:8000/en-US/app/rivendell_app/
```

### Workflow 3: Memory Analysis

```bash
# 1. Acquire memory only
sudo python3 acquisition/python/gandalf.py None Local -M -o /evidence

# 2. Memory analysis with Volatility
python3 analysis/elrond.py MEM-001 /evidence/*.mem /output -MP

# 3. Review processes
cat /output/MEM-001/memory/processes.csv
```

### Workflow 4: Batch Remote Acquisition

```bash
# 1. Create hosts list
cat > acquisition/lists/hosts.list <<EOF
192.168.1.100
192.168.1.101
192.168.1.102
EOF

# 2. Acquire from all hosts
sudo python3 acquisition/python/gandalf.py Password Remote -f acquisition/lists/hosts.list -M

# 3. Batch analyze
for file in /evidence/*.tar.gz; do
    hostname=$(basename "$file" .tar.gz)
    python3 analysis/elrond.py "BATCH-${hostname}" "$file" /output -CPA &
done
wait
```

## 🐛 Troubleshooting

### Docker Issues

```bash
# Restart services
docker-compose restart

# Rebuild images
docker-compose build --no-cache

# View logs
docker-compose logs -f

# Check container status
docker-compose ps

# Clean up and restart
docker-compose down -v
docker-compose up -d
```

### Permission Issues (Acquisition)

```bash
# Ensure running as root
sudo -i

# Check file permissions
ls -la acquisition/

# Make scripts executable
chmod +x acquisition/bash/gandalf.sh
chmod +x acquisition/python/gandalf.py
```

### Import Errors (Analysis)

```bash
# Check dependencies
python3 analysis/cli.py --check-dependencies

# Install missing tools
python3 analysis/cli.py --install

# Verify Python path
echo $PYTHONPATH
export PYTHONPATH=/path/to/rivendell:$PYTHONPATH
```

### Web Interface Not Loading

```bash
# Check if server is running
curl http://localhost:8000/health

# Check ports
netstat -tuln | grep 8000

# View server logs
docker-compose logs rivendell

# Or if running locally
tail -f /var/log/rivendell/web.log
```

## 📚 Next Steps

- **Full Documentation**: See [README.md](README.md)
- **SIEM Setup**: See [docs/SIEM_SETUP.md](docs/SIEM_SETUP.md)
- **Configuration**: See [docs/CONFIG.md](docs/CONFIG.md)
- **Development**: See [docs/CONTRIBUTION.md](docs/CONTRIBUTION.md)

## 🎯 Example Outputs

### Acquisition Output
```
/evidence/
└── hostname.tar.gz
    ├── artefacts/
    │   ├── host.info
    │   ├── memory/hostname.mem
    │   ├── logs/
    │   └── browsers/
    ├── log.audit
    └── log.meta
```

### Analysis Output
```
/output/CASE-001/
├── collected/          # Collected artifacts
├── processed/          # Parsed data (CSV/JSON)
│   ├── timeline.csv
│   ├── registry.csv
│   └── browsers.csv
├── analysis/
│   ├── iocs.csv       # Indicators of Compromise
│   └── keywords.csv
└── splunk/            # Splunk-ready events
    └── events.json
```

## 💡 Pro Tips

1. **Use Docker for easiest setup** - handles all dependencies
2. **Enable memory acquisition** for comprehensive analysis
3. **Use Brisk mode (-B)** for quick triage
4. **Export to SIEM** for long-term storage and correlation
5. **Run acquisition from dedicated forensic workstation**
6. **Use key-based encryption** for sensitive cases
7. **Monitor disk space** - evidence can be large
8. **Review audit logs** after each acquisition

---

**Need Help?** Check the [full documentation](README.md) or open an [issue](https://github.com/cmdaltr/rivendell/issues).

Happy Investigating! 🔍🧙‍♂️

# Example Workflows

## 💡 Common Investigation Workflows

This guide provides practical, real-world workflows for various digital forensic scenarios using the Rivendell DF Acceleration Suite.

---

## 🚨 Incident Response Workflow

### Quick Triage and Analysis

**Scenario:** Suspected compromise requiring rapid investigation

**Steps:**

1. **Quick Triage Acquisition**
   ```bash
   python3 acquisition/python/gandalf.py Password 192.168.1.100 \
     -u administrator \
     -o /evidence/IR-2024-001
   ```

2. **Rapid Analysis**
   ```bash
   elrond -C -c IR-2024-001 \
     -s /evidence/IR-2024-001 \
     -o /cases/IR-2024-001 \
     --Brisk
   ```

3. **Identify Attack Techniques**
   ```bash
   python3 -m rivendell.mitre.mapper /cases/IR-2024-001
   ```

4. **Query for Indicators**
   ```bash
   rivendell-ai query IR-2024-001 "What lateral movement occurred?"
   ```

5. **Export to SIEM for Correlation**
   ```bash
   python3 -m rivendell.siem.splunk_exporter \
     --case-id IR-2024-001 \
     --data-dir /cases/IR-2024-001 \
     --hec-url https://splunk.company.com:8088 \
     --hec-token YOUR_HEC_TOKEN
   ```

6. **Generate Report**
   ```bash
   rivendell-ai summary IR-2024-001 \
     --format markdown \
     --output IR-2024-001-report.md
   ```

---

## 🦠 Malware Analysis Workflow

### Deep Malware Investigation

**Scenario:** Infected system requiring malware analysis

**Steps:**

1. **Acquire Infected System with Memory**
   ```bash
   python3 acquisition/python/gandalf.py Password 192.168.1.50 \
     -u admin \
     -M \
     -o /evidence/MAL-001
   ```

2. **Analyze with Persistence Focus**
   ```bash
   elrond -C -c MAL-001 \
     -s /evidence/MAL-001 \
     -m /evidence/MAL-001/memory.dmp \
     -o /cases/MAL-001 \
     --Analysis \
     --extractIocs \
     --Yara /path/to/yara/rules
   ```

3. **Extract IOCs**
   ```bash
   rivendell-ai query MAL-001 "What IOCs were detected?"
   ```

4. **Identify Malware Behavior**
   ```bash
   rivendell-ai query MAL-001 "What persistence mechanisms were used?"
   rivendell-ai query MAL-001 "What network connections were established?"
   ```

5. **Map to MITRE ATT&CK**
   ```bash
   python3 -m rivendell.mitre.mapper /cases/MAL-001
   python3 -m rivendell.mitre.dashboard \
     -o /cases/MAL-001/attck_matrix.html
   ```

6. **Generate Malware Report**
   ```bash
   rivendell-ai summary MAL-001 \
     --format markdown \
     --output malware_report.md
   ```

---

## ☁️ Cloud Investigation Workflow

### AWS Security Investigation

**Scenario:** Suspicious activity in AWS environment

**Steps:**

1. **Acquire Cloud Logs**
   ```bash
   python3 -m rivendell.cloud.cli aws acquire-logs \
     --days 30 \
     --services cloudtrail,vpc,s3 \
     --output ./logs/AWS-001
   ```

2. **Acquire EC2 Instance Snapshot**
   ```bash
   python3 -m rivendell.cloud.cli aws acquire-disk \
     --instance-id i-1234567890abcdef0 \
     --output ./snapshots/AWS-001
   ```

3. **Analyze CloudTrail Logs**
   ```bash
   python3 -m rivendell.cloud.cli aws analyze-logs \
     --log-file ./logs/AWS-001/cloudtrail.json \
     --output ./analysis/AWS-001
   ```

4. **Index and Query**
   ```bash
   rivendell-ai index AWS-001 ./logs/AWS-001
   rivendell-ai query AWS-001 "What suspicious AWS API calls were made?"
   rivendell-ai query AWS-001 "Show privilege escalation attempts"
   ```

5. **Map Cloud Techniques**
   ```bash
   python3 -m rivendell.mitre.mapper ./analysis/AWS-001
   ```

6. **Generate Investigation Report**
   ```bash
   rivendell-ai summary AWS-001 \
     --format markdown \
     --output aws_investigation.md
   ```

---

## 👤 Insider Threat Investigation

### User Activity Analysis

**Scenario:** Suspected data exfiltration by insider

**Steps:**

1. **Acquire User Workstation**
   ```bash
   python3 acquisition/python/gandalf.py Password 192.168.1.75 \
     -u investigator \
     --Userprofiles \
     -o /evidence/INSIDER-001
   ```

2. **Full Analysis with Timeline**
   ```bash
   elrond -C -c INSIDER-001 \
     -s /evidence/INSIDER-001 \
     -o /cases/INSIDER-001 \
     --Timeline \
     --Analysis \
     --collectFiles "*.pdf,*.docx,*.xlsx,*.zip"
   ```

3. **Query User Activity**
   ```bash
   rivendell-ai query INSIDER-001 "What files were accessed by the user?"
   rivendell-ai query INSIDER-001 "Show USB device usage"
   rivendell-ai query INSIDER-001 "What files were copied to external media?"
   ```

4. **Analyze Browser History**
   ```bash
   python3 -m rivendell.artifacts.browsers.chrome \
     /cases/INSIDER-001/artifacts/Users/*/AppData/Local/Google/Chrome
   ```

5. **Check Cloud Storage Activity**
   ```bash
   rivendell-ai query INSIDER-001 "Show Dropbox/OneDrive activity"
   ```

6. **Generate Timeline Report**
   ```bash
   rivendell-ai summary INSIDER-001 \
     --format timeline \
     --output insider_timeline.md
   ```

---

## 🌐 Web Application Breach

### Web Server Forensics

**Scenario:** Web application compromise investigation

**Steps:**

1. **Acquire Web Server**
   ```bash
   python3 acquisition/python/gandalf.py Password webserver.company.com \
     -u webadmin \
     -o /evidence/WEB-001
   ```

2. **Analyze Web Server Logs**
   ```bash
   elrond -C -c WEB-001 \
     -s /evidence/WEB-001 \
     -o /cases/WEB-001 \
     --Analysis \
     --extractIocs
   ```

3. **Query for Web Attacks**
   ```bash
   rivendell-ai query WEB-001 "Show SQL injection attempts"
   rivendell-ai query WEB-001 "What webshells were detected?"
   rivendell-ai query WEB-001 "Show suspicious POST requests"
   ```

4. **Extract IOCs**
   ```bash
   python3 -m rivendell.iocs.extractor \
     /cases/WEB-001 \
     --output /cases/WEB-001/iocs.json
   ```

5. **Check for Backdoors**
   ```bash
   rivendell-ai query WEB-001 "What PHP/ASPX files were modified?"
   ```

6. **Generate Breach Report**
   ```bash
   rivendell-ai summary WEB-001 \
     --format markdown \
     --output web_breach_report.md
   ```

---

## 📧 Email Investigation

### Phishing Campaign Analysis

**Scenario:** Phishing email investigation

**Steps:**

1. **Acquire Email Server Data**
   ```bash
   python3 acquisition/python/gandalf.py Password mailserver.company.com \
     -u mailadmin \
     -o /evidence/PHISH-001
   ```

2. **Parse Email Artifacts**
   ```bash
   elrond -C -c PHISH-001 \
     -s /evidence/PHISH-001 \
     -o /cases/PHISH-001 \
     --Analysis
   ```

3. **Query Email Patterns**
   ```bash
   rivendell-ai query PHISH-001 "Show suspicious email attachments"
   rivendell-ai query PHISH-001 "What URLs were in phishing emails?"
   rivendell-ai query PHISH-001 "Show email senders from external domains"
   ```

4. **Extract Email IOCs**
   ```bash
   python3 -m rivendell.artifacts.email.parser \
     /cases/PHISH-001 \
     --extract-urls \
     --extract-attachments
   ```

5. **Correlate with User Clicks**
   ```bash
   rivendell-ai query PHISH-001 "Which users clicked phishing links?"
   ```

6. **Generate Phishing Report**
   ```bash
   rivendell-ai summary PHISH-001 \
     --format markdown \
     --output phishing_report.md
   ```

---

## 🔐 Ransomware Response

### Ransomware Investigation and Recovery

**Scenario:** Ransomware incident requiring investigation

**Steps:**

1. **Rapid Acquisition (Memory Priority)**
   ```bash
   python3 acquisition/python/gandalf.py Password 192.168.1.100 \
     -u admin \
     -M \
     --vss \
     -o /evidence/RANSOM-001
   ```

2. **Memory Analysis First**
   ```bash
   python3 -m volatility3 -f /evidence/RANSOM-001/memory.dmp \
     windows.pslist \
     windows.pstree \
     windows.netstat \
     windows.filescan | grep -i "\.encrypt\|\.locked\|\.crypto"
   ```

3. **Full Disk Analysis**
   ```bash
   elrond -C -c RANSOM-001 \
     -s /evidence/RANSOM-001 \
     -m /evidence/RANSOM-001/memory.dmp \
     -o /cases/RANSOM-001 \
     --vss \
     --extractIocs
   ```

4. **Identify Ransomware Variant**
   ```bash
   rivendell-ai query RANSOM-001 "What ransomware strain was detected?"
   rivendell-ai query RANSOM-001 "Show encryption activity timeline"
   ```

5. **Find Patient Zero**
   ```bash
   rivendell-ai query RANSOM-001 "What was the initial infection vector?"
   rivendell-ai query RANSOM-001 "Show lateral movement from patient zero"
   ```

6. **Check for Shadow Copies**
   ```bash
   python3 -m rivendell.artifacts.windows.vss \
     /cases/RANSOM-001 \
     --list-snapshots
   ```

7. **Generate Response Report**
   ```bash
   rivendell-ai summary RANSOM-001 \
     --format markdown \
     --output ransomware_response.md
   ```

---

## 🔎 Data Recovery

### Deleted File Recovery

**Scenario:** Critical file recovery from disk

**Steps:**

1. **Acquire Disk Image**
   ```bash
   sudo dd if=/dev/sdb of=/evidence/RECOVERY-001/disk.dd bs=4M status=progress
   ```

2. **Analyze with File Carving**
   ```bash
   elrond -C -c RECOVERY-001 \
     -s /evidence/RECOVERY-001/disk.dd \
     -o /cases/RECOVERY-001 \
     --collectFiles "*.pdf,*.docx,*.xlsx" \
     --exhaustive
   ```

3. **Query for Deleted Files**
   ```bash
   rivendell-ai query RECOVERY-001 "Show deleted PDF files"
   rivendell-ai query RECOVERY-001 "What files were deleted in the last week?"
   ```

4. **Bulk Extract Files**
   ```bash
   python3 -m rivendell.recovery.bulk_extractor \
     /cases/RECOVERY-001 \
     --output /cases/RECOVERY-001/recovered
   ```

5. **Generate Recovery Report**
   ```bash
   rivendell-ai summary RECOVERY-001 \
     --format markdown \
     --output recovery_report.md
   ```

---

## 📱 Mobile Device Investigation

### Android Forensics (Future Feature)

**Coming in v2.2**

```bash
# Acquire Android device
python3 acquisition/python/gandalf.py --mobile android \
  --device-id ABC123 \
  -o /evidence/MOBILE-001

# Analyze Android artifacts
elrond -C -c MOBILE-001 \
  -s /evidence/MOBILE-001 \
  -o /cases/MOBILE-001 \
  --mobile android
```

---

## 🐳 Container Forensics

### Docker Investigation (Future Feature)

**Coming in v2.3**

```bash
# Acquire container
python3 -m rivendell.containers.docker acquire \
  --container-id abc123 \
  -o /evidence/DOCKER-001

# Analyze container
elrond -C -c DOCKER-001 \
  -s /evidence/DOCKER-001 \
  -o /cases/DOCKER-001 \
  --container docker
```

---

## 📊 Workflow Templates

### Custom Workflow Template

Create custom workflows for your organization:

```bash
# Create workflow template
cat > /etc/rivendell/workflows/company_ir.yml <<EOF
name: "Company IR Workflow"
description: "Standard incident response workflow"
steps:
  - name: "Acquisition"
    command: "gandalf.py {password} {target} -u {user} -o {output}"
  - name: "Analysis"
    command: "elrond -C -c {case_id} -s {source} -o {output}"
  - name: "MITRE Mapping"
    command: "python3 -m rivendell.mitre.mapper {output}"
  - name: "AI Query"
    command: "rivendell-ai query {case_id} {query}"
  - name: "Report"
    command: "rivendell-ai summary {case_id} --format markdown"
EOF

# Execute workflow
python3 -m rivendell.workflows.executor \
  --template /etc/rivendell/workflows/company_ir.yml \
  --case-id IR-2024-001
```

---

## 🔄 Automated Workflows

### Scheduled Analysis

```bash
# Create cron job for daily log analysis
crontab -e

# Add daily analysis at 2 AM
0 2 * * * /usr/local/bin/rivendell-analyze-daily.sh

# Create analysis script
cat > /usr/local/bin/rivendell-analyze-daily.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
CASE_ID="AUTO-$DATE"

elrond -C -c $CASE_ID \
  -s /var/log \
  -o /cases/$CASE_ID \
  --Analysis

python3 -m rivendell.mitre.mapper /cases/$CASE_ID

rivendell-ai summary $CASE_ID \
  --format email \
  --send-to security@company.com
EOF

chmod +x /usr/local/bin/rivendell-analyze-daily.sh
```

---

## 📚 Additional Resources

- **[Usage Guide](USAGE.md)** - Complete command reference
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive documentation
- **[Configuration](docs/CONFIG.md)** - Configuration options
- **[Support](docs/SUPPORT.md)** - Troubleshooting

---

**See:** [README.md](README.md) for overview and quick start

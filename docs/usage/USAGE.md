# Usage Guide

## 📖 Complete Command Reference

This guide provides comprehensive command references for all Rivendell DF Acceleration Suite features across all supported platforms and languages.

---

## 🧙 Gandalf - Remote Acquisition

### Basic Acquisition

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Python - Basic Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 acquisition/python/gandalf.py Password 192.168.1.100 -u admin -o /evidence/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Bash - Basic Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>./acquisition/bash/gandalf.sh 192.168.1.100 admin Password /evidence/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/powershell.png" alt="PowerShell" width="42"/></td>
      <td><strong>PowerShell - Basic Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>.\acquisition\powershell\Gandalf.ps1 -Target 192.168.1.100 -Username admin -Password Password -OutputDir C:\Evidence\CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Acquisition with Memory

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Python - Memory Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 acquisition/python/gandalf.py Password 192.168.1.100 -u admin -M -o /evidence/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Bash - Memory Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>./acquisition/bash/gandalf.sh 192.168.1.100 admin Password /evidence/CASE-001 --memory</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/powershell.png" alt="PowerShell" width="42"/></td>
      <td><strong>PowerShell - Memory Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>.\acquisition\powershell\Gandalf.ps1 -Target 192.168.1.100 -Username admin -Password Password -OutputDir C:\Evidence\CASE-001 -IncludeMemory</code>
      </td>
    </tr>
  </table>
</div>

### Complete Acquisition Options

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Python - Full Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 acquisition/python/gandalf.py Password 192.168.1.100 \
  -u admin \
  -M \                    # Include memory dump
  --vss \                 # Include Volume Shadow Copies
  --Userprofiles \        # Collect user profiles
  --encrypt \             # Encrypt evidence
  -o /evidence/CASE-001</pre>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Bash - Full Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>./acquisition/bash/gandalf.sh 192.168.1.100 admin Password /evidence/CASE-001 \
  --memory \
  --vss \
  --userprofiles \
  --encrypt</pre>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/powershell.png" alt="PowerShell" width="42"/></td>
      <td><strong>PowerShell - Full Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>.\acquisition\powershell\Gandalf.ps1 `
  -Target 192.168.1.100 `
  -Username admin `
  -Password Password `
  -OutputDir C:\Evidence\CASE-001 `
  -IncludeMemory `
  -IncludeVSS `
  -IncludeUserProfiles `
  -Encrypt</pre>
      </td>
    </tr>
  </table>
</div>

### Local Acquisition

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Python - Local Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>sudo python3 acquisition/python/gandalf.py --local -o /evidence/LOCAL-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Bash - Local Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>sudo ./acquisition/bash/gandalf.sh --local /evidence/LOCAL-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/powershell.png" alt="PowerShell" width="42"/></td>
      <td><strong>PowerShell - Local Acquisition</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>.\acquisition\powershell\Gandalf.ps1 -Local -OutputDir C:\Evidence\LOCAL-001</code>
      </td>
    </tr>
  </table>
</div>

---

## 🧝‍♂️ Elrond - Forensic Analysis

### Basic Analysis

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Python - Basic Analysis</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Bash - Basic Analysis</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/powershell.png" alt="PowerShell" width="42"/></td>
      <td><strong>PowerShell - Basic Analysis</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond CASE-001 C:\Evidence\disk.E01 C:\Output\CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Collection Mode

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Collection with Analysis</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C --Collect CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Processing Mode

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Process Artifacts</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -P --Process CASE-001 /evidence/artifacts /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Analysis Mode

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Full Analysis</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -A --Analysis CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Combined Workflow

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Collect, Process, and Analyze</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>elrond -C -P -A CASE-001 /evidence/disk.E01 /output/CASE-001</pre>
      </td>
    </tr>
  </table>
</div>

### Memory Analysis

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Include Memory Analysis</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -M --Memory CASE-001 /evidence/disk.E01 /output/CASE-001 -m /evidence/memory.dmp</code>
      </td>
    </tr>
  </table>
</div>

### Timeline Generation

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Generate Timeline</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -T --Timeline CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### IOC Extraction

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Extract Indicators of Compromise</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -I --extractIocs CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### YARA Scanning

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Scan with YARA Rules</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -Y --Yara /path/to/yara/rules CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Keyword Search

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Search with Keywords</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -K --Keywords /path/to/keywords.txt CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### VSS Processing

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Process Volume Shadow Copies</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -c --vss CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### User Profile Collection

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Collect User Profiles</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -U --Userprofiles CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Speed Modes

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Quick Analysis (Fast)</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -q --quick CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Super Quick (Fastest)</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -Q --superQuick CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Brisk (Balanced)</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -B --Brisk CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Exhaustive (Thorough)</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -X --eXhaustive CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### SIEM Export

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Export to Splunk</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -S --Splunk CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Export to Elasticsearch</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -E --Elastic CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### MITRE ATT&CK Navigator

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Generate ATT&CK Navigator Layer</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond -C -P -A -N --Navigator CASE-001 /evidence/disk.E01 /output/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Complete Workflow Example

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Full Forensic Workflow</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>elrond -C -P -A -M -T -I -c -U -B -N -S \
  CASE-001 \
  /evidence/disk.E01 \
  /output/CASE-001 \
  -m /evidence/memory.dmp</pre>
      </td>
    </tr>
  </table>
</div>

---

## 🎯 MITRE ATT&CK Integration

### Update MITRE Data

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Update ATT&CK Framework</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.mitre.updater</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Update via Script</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>./scripts/update_mitre.sh</code>
      </td>
    </tr>
  </table>
</div>

### Map Artifacts to Techniques

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Map to ATT&CK</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.mitre.mapper /cases/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Generate Dashboard

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Generate ATT&CK Dashboard</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.mitre.dashboard -o /output/dashboard.html</code>
      </td>
    </tr>
  </table>
</div>

### Generate Navigator Layer

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Create Navigator Layer</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.mitre.navigator /cases/CASE-001 -o navigator_layer.json</code>
      </td>
    </tr>
  </table>
</div>

---

## 📊 Coverage Analysis

### Analyze Coverage

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Analyze ATT&CK Coverage</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.coverage.analyzer /cases/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Real-Time Monitoring

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Monitor Coverage in Real-Time</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.coverage.monitor --watch /cases</code>
      </td>
    </tr>
  </table>
</div>

### Generate Coverage Dashboard

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Create Coverage Dashboard</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.coverage.dashboard -o dashboard.html</code>
      </td>
    </tr>
  </table>
</div>

---

## ☁️ Cloud Forensics

### AWS Commands

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>List AWS Instances</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.cloud.cli aws list --credentials aws_creds.json</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Acquire EC2 Disk Snapshot</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.cloud.cli aws acquire-disk \
  --instance-id i-1234567890abcdef0 \
  --output ./snapshots/AWS-001</pre>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Acquire CloudTrail Logs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.cloud.cli aws acquire-logs \
  --days 30 \
  --services cloudtrail,vpc,s3 \
  --output ./logs/AWS-001</pre>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Analyze CloudTrail</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.cloud.cli aws analyze-logs \
  --log-file cloudtrail.json \
  --output ./analysis</pre>
      </td>
    </tr>
  </table>
</div>

### Azure Commands

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>List Azure VMs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.cloud.cli azure list --credentials azure_creds.json</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Acquire Azure VM Disk</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.cloud.cli azure acquire-disk \
  --instance-id myvm \
  --resource-group mygroup \
  --output ./snapshots/AZURE-001</pre>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Acquire Activity Logs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.cloud.cli azure acquire-logs \
  --days 30 \
  --output ./logs/AZURE-001</pre>
      </td>
    </tr>
  </table>
</div>

### GCP Commands

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>List GCP Instances</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.cloud.cli gcp list --credentials gcp_creds.json</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Acquire GCP Disk Snapshot</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.cloud.cli gcp acquire-disk \
  --instance-id myinstance \
  --zone us-central1-a \
  --output ./snapshots/GCP-001</pre>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Acquire Cloud Logging</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.cloud.cli gcp acquire-logs \
  --days 30 \
  --output ./logs/GCP-001</pre>
      </td>
    </tr>
  </table>
</div>

---

## 🤖 AI-Powered Analysis

### Index Case Data

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Index Investigation Data</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai index CASE-001 /cases/CASE-001</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Index via Script</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>./scripts/ai_index.sh CASE-001 /cases/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Query Case

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Natural Language Query</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai query CASE-001 "What PowerShell commands were executed?"</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Query Network Activity</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai query CASE-001 "Show network connections to external IPs"</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Query ATT&CK Techniques</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai query CASE-001 "What MITRE ATT&CK techniques were detected?"</code>
      </td>
    </tr>
  </table>
</div>

### Get Investigation Suggestions

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Get AI Suggestions</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai suggest CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Generate Summary

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Generate Markdown Summary</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai summary CASE-001 --format markdown --output summary.md</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Generate HTML Report</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai summary CASE-001 --format html --output report.html</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Generate JSON Report</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai summary CASE-001 --format json --output report.json</code>
      </td>
    </tr>
  </table>
</div>

### Web Interface

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Start Web Chat Interface</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.ai.web_interface</code>
      </td>
    </tr>
    <tr>
      <td colspan="2">
        <em>Access at: http://localhost:5687/ai/chat/CASE-001</em>
      </td>
    </tr>
  </table>
</div>

---

## 📤 SIEM Integration

### Splunk Export

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Export to Splunk HEC</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.siem.splunk_exporter \
  --case-id CASE-001 \
  --data-dir /cases/CASE-001 \
  --hec-url https://splunk:8088 \
  --hec-token YOUR_HEC_TOKEN</pre>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Export via Script</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>./scripts/export_splunk.sh CASE-001 /cases/CASE-001</code>
      </td>
    </tr>
  </table>
</div>

### Elasticsearch Export

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Export to Elasticsearch</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <pre>python3 -m rivendell.siem.elastic_exporter \
  --case-id CASE-001 \
  --data-dir /cases/CASE-001 \
  --elastic-url https://elastic:9200 \
  --index rivendell-case-001</pre>
      </td>
    </tr>
  </table>
</div>

---

## 🔍 Artifact Parsing

### Windows Artifacts

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse WMI Persistence</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.windows.wmi /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Scheduled Tasks</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.windows.tasks /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Windows Services</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.windows.services /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Registry</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.windows.registry /path/to/registry/hives</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Event Logs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.windows.evtx /path/to/event/logs</code>
      </td>
    </tr>
  </table>
</div>

### macOS Artifacts

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Launch Agents/Daemons</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.macos.launch_agents /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Unified Logs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.macos.unified_logs /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse FSEvents</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.macos.fsevents /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Plists</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.macos.plists /path/to/plists</code>
      </td>
    </tr>
  </table>
</div>

### Linux Artifacts

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Systemd Services</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.linux.systemd /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Cron Jobs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.linux.cron /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Bash History</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.linux.bash_history /path/to/system</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Parse Auth Logs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 -m rivendell.artifacts.linux.auth_logs /path/to/logs</code>
      </td>
    </tr>
  </table>
</div>

---

## 🐳 Docker Deployment

### Start Services

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Start All Services</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>docker-compose up -d</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Start Specific Service</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>docker-compose up -d rivendell</code>
      </td>
    </tr>
  </table>
</div>

### Stop Services

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Stop All Services</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>docker-compose down</code>
      </td>
    </tr>
  </table>
</div>

### View Logs

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>View Service Logs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>docker-compose logs -f rivendell</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>View Celery Worker Logs</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>docker-compose logs -f celery-worker</code>
      </td>
    </tr>
  </table>
</div>

### Build Images

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Build All Images</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>docker-compose build</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/bash.png" alt="Bash" width="42"/></td>
      <td><strong>Rebuild Without Cache</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>docker-compose build --no-cache</code>
      </td>
    </tr>
  </table>
</div>

---

## 🔧 Utility Commands

### Check Dependencies

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Verify Installation</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond --check-dependencies</code>
      </td>
    </tr>
  </table>
</div>

### Version Information

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Show Version</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond --version</code>
      </td>
    </tr>
  </table>
</div>

### Help

<div align="left">
  <table>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Show Help</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>elrond --help</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>Gandalf Help</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>python3 acquisition/python/gandalf.py --help</code>
      </td>
    </tr>
    <tr>
      <td><img src="./docs/images/readme/python.png" alt="Python" width="42"/></td>
      <td><strong>AI Agent Help</strong></td>
    </tr>
    <tr>
      <td colspan="2">
        <code>rivendell-ai --help</code>
      </td>
    </tr>
  </table>
</div>

---

## 📚 Additional Resources

- **[Workflows](WORKFLOWS.md)** - Common investigation workflows
- **[Requirements](REQUIREMENTS.md)** - Installation and dependencies
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive documentation
- **[Quick Start](QUICKSTART.md)** - Get started quickly
- **[Support](docs/SUPPORT.md)** - Troubleshooting and help

---

**See:** [README.md](README.md) for overview and feature descriptions

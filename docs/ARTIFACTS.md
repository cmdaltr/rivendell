# Artifact Parsing - Rivendell DFIR Suite

**Version:** 2.1.0

## Overview

Rivendell provides comprehensive artifact parsing capabilities across Windows, macOS, and Linux systems. This document covers all supported artifact types and their analysis methods.

---

## Table of Contents

1. [Windows Artifacts](#windows-artifacts)
2. [macOS Artifacts](#macos-artifacts)
3. [Linux Artifacts](#linux-artifacts)
4. [Cross-Platform Artifacts](#cross-platform-artifacts)
5. [Usage Examples](#usage-examples)

---

## Windows Artifacts

### Registry Analysis

**Supported Hives:**
- SAM - User accounts and password hashes
- SYSTEM - System configuration
- SOFTWARE - Installed applications
- SECURITY - Security policies and audit settings
- NTUSER.DAT - User-specific settings
- UsrClass.dat - Shell items and recent files

**Key Areas Analyzed:**
- AutoRun locations (Run, RunOnce, Services)
- Installed software and patches
- USB device history
- Network configuration
- Recent files and programs
- User accounts and groups
- Shellbags (folder access history)

**MITRE ATT&CK Mapping:**
- T1547.001 - Registry Run Keys / Startup Folder
- T1112 - Modify Registry
- T1059 - Command and Scripting Interpreter

**Usage:**
```bash
# Parse registry with Elrond
elrond -C -c CASE-001 -s /evidence --registry-only -o /output

# Query registry with AI
rivendell-ai query CASE-001 "What registry persistence mechanisms exist?"
```

### Event Logs

**Supported Log Types:**
- Security.evtx - Logon/logoff, privilege use
- System.evtx - System events, service control
- Application.evtx - Application events
- PowerShell logs - Script execution
- Sysmon logs - Detailed process and network events
- Windows Defender logs - Malware detection

**Key Events:**
- 4624/4625 - Successful/Failed logons
- 4672 - Admin logon
- 4688 - Process creation
- 4698 - Scheduled task created
- 7045 - Service installed
- PowerShell script block logging

**MITRE ATT&CK Mapping:**
- T1070.001 - Clear Windows Event Logs
- T1059.001 - PowerShell
- T1053.005 - Scheduled Task

**Usage:**
```bash
# Parse event logs
elrond -C -c CASE-001 -s /evidence --evtx-only -o /output

# Query events
rivendell-ai query CASE-001 "Show failed login attempts"
```

### Prefetch Files

**Information Extracted:**
- Application execution history
- Execution count
- Last execution times (up to 8)
- Files and directories accessed
- Volume information

**MITRE ATT&CK Mapping:**
- T1059 - Command and Scripting Interpreter
- T1204 - User Execution

**Usage:**
```bash
# Parse prefetch
python3 -m rivendell.artifacts.windows.prefetch /path/to/Prefetch

# Query execution history
rivendell-ai query CASE-001 "What executables ran most frequently?"
```

### Master File Table (MFT)

**Information Extracted:**
- File metadata (creation, modification, access times)
- File attributes
- File resident data
- Deleted file records
- File ownership

**MITRE ATT&CK Mapping:**
- T1070.004 - File Deletion
- T1564.001 - Hidden Files and Directories

**Usage:**
```bash
# Parse MFT
python3 -m rivendell.artifacts.windows.mft /path/to/$MFT

# Timeline analysis
elrond -C -c CASE-001 -s /evidence -t -o /output
```

### USN Journal

**Information Extracted:**
- File system change history
- File creation, deletion, renaming
- Timestamped file operations

**Usage:**
```bash
# Parse USN journal
python3 -m rivendell.artifacts.windows.usn /path/to/$UsnJrnl
```

### WMI Persistence

**Analyzed Components:**
- WMI Event Consumers
- WMI Event Filters
- WMI Filter-to-Consumer Bindings
- WMI Permanent Subscriptions

**MITRE ATT&CK Mapping:**
- T1546.003 - Windows Management Instrumentation Event Subscription

**Usage:**
```bash
# Parse WMI
python3 -m rivendell.artifacts.windows.wmi /path/to/system

# Detect WMI persistence
rivendell-ai query CASE-001 "Are there WMI persistence mechanisms?"
```

### Scheduled Tasks

**Information Extracted:**
- Task names and descriptions
- Execution triggers
- Actions and commands
- User context
- Creation and modification times

**MITRE ATT&CK Mapping:**
- T1053.005 - Scheduled Task/Job: Scheduled Task

**Usage:**
```bash
# Parse scheduled tasks
python3 -m rivendell.artifacts.windows.tasks /path/to/Tasks

# Query tasks
rivendell-ai query CASE-001 "Show suspicious scheduled tasks"
```

### Services

**Information Extracted:**
- Service names and descriptions
- Binary paths
- Service types and start modes
- Dependencies
- Service accounts

**MITRE ATT&CK Mapping:**
- T1543.003 - Create or Modify System Process: Windows Service

**Usage:**
```bash
# Parse services
python3 -m rivendell.artifacts.windows.services /path/to/system
```

### Browser Artifacts

**Supported Browsers:**
- Chrome/Chromium
- Firefox
- Edge
- Internet Explorer

**Data Extracted:**
- Browsing history
- Downloads
- Cookies
- Cache
- Form autofill data
- Bookmarks

**MITRE ATT&CK Mapping:**
- T1539 - Steal Web Session Cookie
- T1213 - Data from Information Repositories

**Usage:**
```bash
# Parse browser artifacts
elrond -C -c CASE-001 -s /evidence --browser-only -o /output

# Query browsing
rivendell-ai query CASE-001 "What malicious websites were visited?"
```

---

## macOS Artifacts

### Property Lists (plists)

**Key plists:**
- LaunchAgents - User-level persistence
- LaunchDaemons - System-level persistence
- Login Items - Login persistence
- Preferences - Application settings

**MITRE ATT&CK Mapping:**
- T1543.001 - Launch Agent
- T1543.004 - Launch Daemon

**Usage:**
```bash
# Parse plists
python3 -m rivendell.artifacts.macos.plists /path/to/system

# Query persistence
rivendell-ai query CASE-001 "What macOS persistence mechanisms exist?"
```

### Launch Agents and Daemons

**Locations Analyzed:**
- ~/Library/LaunchAgents
- /Library/LaunchAgents
- /System/Library/LaunchAgents
- /Library/LaunchDaemons
- /System/Library/LaunchDaemons

**Information Extracted:**
- Program paths
- Arguments
- Run conditions
- Keep-alive settings
- User context

**Usage:**
```bash
# Parse launch items
python3 -m rivendell.artifacts.macos.launch_agents /path/to/system
```

### Unified Logs

**Log Types:**
- System logs
- Application logs
- Security logs
- Install logs

**Usage:**
```bash
# Parse unified logs
python3 -m rivendell.artifacts.macos.unified_logs /path/to/system

# Timeline integration
elrond -C -c CASE-001 -s /evidence -t -o /output
```

### FSEvents

**Information Extracted:**
- File system events
- File creation, modification, deletion
- Folder operations
- Historical file system activity

**Usage:**
```bash
# Parse FSEvents
python3 -m rivendell.artifacts.macos.fsevents /path/to/.fseventsd
```

### Spotlight Database

**Information Extracted:**
- File metadata index
- Search history
- Application usage

**Usage:**
```bash
# Parse Spotlight
python3 -m rivendell.artifacts.macos.spotlight /path/to/system
```

### Bash History

**Information Extracted:**
- Command history
- Timestamps (if HISTTIMEFORMAT set)
- User activity patterns

**MITRE ATT&CK Mapping:**
- T1070.003 - Clear Command History
- T1059.004 - Unix Shell

**Usage:**
```bash
# Parse bash history
python3 -m rivendell.artifacts.macos.bash_history /path/to/.bash_history

# Query commands
rivendell-ai query CASE-001 "What bash commands were executed?"
```

---

## Linux Artifacts

### System Logs

**Key Log Files:**
- /var/log/syslog - General system messages
- /var/log/auth.log - Authentication logs
- /var/log/kern.log - Kernel messages
- /var/log/messages - General messages
- /var/log/secure - Security/authentication (RHEL/CentOS)

**Information Extracted:**
- Login attempts
- Service starts/stops
- System errors
- Security events

**MITRE ATT&CK Mapping:**
- T1070.002 - Clear Linux or Mac System Logs

**Usage:**
```bash
# Parse system logs
python3 -m rivendell.artifacts.linux.syslog /path/to/var/log

# Query logs
rivendell-ai query CASE-001 "Show failed SSH attempts"
```

### systemd Services

**Information Extracted:**
- Service unit files
- Service states
- Dependencies
- Timers (scheduled tasks)

**MITRE ATT&CK Mapping:**
- T1543.002 - Systemd Service

**Usage:**
```bash
# Parse systemd services
python3 -m rivendell.artifacts.linux.systemd /path/to/system
```

### Cron Jobs

**Locations Analyzed:**
- /etc/crontab
- /etc/cron.d/
- /var/spool/cron/
- User crontabs

**MITRE ATT&CK Mapping:**
- T1053.003 - Cron

**Usage:**
```bash
# Parse cron
python3 -m rivendell.artifacts.linux.cron /path/to/system

# Query scheduled tasks
rivendell-ai query CASE-001 "What cron jobs exist?"
```

### Bash History

**Information Extracted:**
- Command history per user
- Timestamps (if configured)
- Root and user activity

**Usage:**
```bash
# Parse bash history
python3 -m rivendell.artifacts.linux.bash_history /path/to/home
```

### SSH Logs and Keys

**Information Extracted:**
- SSH login attempts
- Successful/failed authentications
- Authorized keys
- Known hosts
- SSH configuration

**MITRE ATT&CK Mapping:**
- T1021.004 - SSH
- T1552.004 - Private Keys

**Usage:**
```bash
# Parse SSH artifacts
python3 -m rivendell.artifacts.linux.ssh /path/to/system
```

### Package Manager Logs

**Supported:**
- apt (Debian/Ubuntu)
- yum/dnf (RHEL/CentOS/Fedora)
- pacman (Arch)

**Information Extracted:**
- Installed packages
- Installation timestamps
- Package versions
- Update history

**Usage:**
```bash
# Parse package logs
python3 -m rivendell.artifacts.linux.packages /path/to/system
```

---

## Cross-Platform Artifacts

### Memory Dumps

**Analyzed with Volatility 3:**
- Running processes
- Network connections
- Loaded DLLs/libraries
- Open files
- Registry hives (Windows)
- Command history
- Injected code
- Rootkit detection

**MITRE ATT&CK Mapping:**
- T1003 - OS Credential Dumping
- T1055 - Process Injection
- T1620 - Reflective Code Loading

**Usage:**
```bash
# Analyze memory
elrond -C -c CASE-001 -s /evidence -m /memory.dmp -o /output

# Query memory
rivendell-ai query CASE-001 "What processes were running in memory?"
```

### Network Artifacts

**Information Extracted:**
- Active connections
- Connection history
- DNS queries
- DHCP leases
- ARP cache
- Firewall rules

**Usage:**
```bash
# Parse network artifacts
python3 -m rivendell.artifacts.network /path/to/system

# Query connections
rivendell-ai query CASE-001 "Show connections to external IPs"
```

### Timeline Generation

**Sources:**
- File system metadata (MFT, FSEvents)
- Event logs
- Registry
- Browser history
- Application logs
- Memory artifacts

**Usage:**
```bash
# Generate timeline
elrond -C -c CASE-001 -s /evidence -t -o /output

# Query timeline
rivendell-ai query CASE-001 "What happened between 14:00 and 15:00?"
```

---

## Usage Examples

### Complete Artifact Analysis

```bash
# Full analysis with all artifacts
elrond -C -c CASE-001 \
  -s /evidence \
  -m /evidence/memory.dmp \
  -t \
  -o /output \
  --veryverbose

# Index for AI
rivendell-ai index CASE-001 /output

# Query artifacts
rivendell-ai query CASE-001 "What persistence mechanisms were found?"
```

### Targeted Artifact Extraction

```bash
# Registry only
elrond -C -c CASE-001 -s /evidence --registry-only -o /output

# Event logs only
elrond -C -c CASE-001 -s /evidence --evtx-only -o /output

# Browser artifacts only
elrond -C -c CASE-001 -s /evidence --browser-only -o /output
```

### Platform-Specific Analysis

```bash
# Windows artifacts
python3 -m rivendell.artifacts.windows.analyze /evidence/windows

# macOS artifacts
python3 -m rivendell.artifacts.macos.analyze /evidence/macos

# Linux artifacts
python3 -m rivendell.artifacts.linux.analyze /evidence/linux
```

### AI-Powered Queries

```bash
# Persistence analysis
rivendell-ai query CASE-001 "What persistence mechanisms exist?"

# Execution analysis
rivendell-ai query CASE-001 "What PowerShell commands were executed?"

# Network analysis
rivendell-ai query CASE-001 "Show network connections to suspicious IPs"

# Timeline analysis
rivendell-ai query CASE-001 "Summarize activity on 2024-01-15"
```

---

## Best Practices

### Evidence Collection

1. **Maintain integrity** - Use write-blockers and document hashing
2. **Collect comprehensively** - Get all relevant artifact types
3. **Document process** - Log all acquisition steps
4. **Preserve timestamps** - Use forensically sound methods

### Analysis Workflow

1. **Start with triage** - Quick analysis of high-value artifacts
2. **Build timeline** - Reconstruct events chronologically
3. **Identify anomalies** - Look for unusual patterns
4. **Correlate artifacts** - Cross-reference multiple sources
5. **Map to MITRE** - Understand attack techniques used

### Using AI for Analysis

1. **Index thoroughly** - Include all relevant artifacts
2. **Ask specific questions** - Get better answers with context
3. **Verify AI findings** - Cross-check with raw artifacts
4. **Iterate queries** - Use follow-up questions
5. **Document insights** - Save important findings

---

## Supported Tools

Rivendell integrates these artifact parsing tools:

- **RegRipper** - Registry analysis
- **EvtxCmd** - Event log parsing
- **Plaso/log2timeline** - Timeline generation
- **Volatility 3** - Memory forensics
- **Bulk Extractor** - IOC extraction
- **MFTECmd** - MFT parsing
- **PECmd** - Prefetch analysis
- **And 20+ more tools**

See [TOOLS.md](TOOLS.md) for the complete list.

---

## References

- **MITRE ATT&CK**: https://attack.mitre.org/
- **Forensics Wiki**: https://forensicswiki.org/
- **SANS DFIR**: https://www.sans.org/digital-forensics-incident-response/

---

**Version:** 2.1.0
**Last Updated:** 2025-11-12

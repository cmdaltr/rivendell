# Rivendell Advanced Features Implementation Guide

**Version**: 2.1.0
**Date**: 2025-11-12
**Status**: Planning & Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Feature 1: Latest MITRE ATT&CK Integration](#feature-1-latest-mitre-attck-integration)
3. [Feature 2: Standalone MITRE Coverage Analysis](#feature-2-standalone-mitre-coverage-analysis)
4. [Feature 3: Enhanced Artifact Parsing](#feature-3-enhanced-artifact-parsing)
5. [Feature 4: Cloud Forensics Support](#feature-4-cloud-forensics-support)
6. [Feature 5: AI-Powered Analysis Agent](#feature-5-ai-powered-analysis-agent)
7. [Implementation Timeline](#implementation-timeline)
8. [Dependencies](#dependencies)
9. [Testing Strategy](#testing-strategy)

---

## Overview

This guide outlines the implementation of five major enhancements to Rivendell DFIR Suite:

### Goals

1. **Always-Current MITRE ATT&CK**: Auto-update to latest ATT&CK framework
2. **Independent Coverage Analysis**: Generate ATT&CK coverage without SIEM ingestion
3. **Enhanced Artifact Support**: WMI, macOS, Linux artifact parsing
4. **Cloud Forensics**: Support for AWS, Azure, GCP forensic artifacts
5. **AI-Powered Analysis**: Intelligent query system for investigation data

### Success Criteria

- ✅ Automatic MITRE ATT&CK updates (weekly)
- ✅ Real-time coverage dashboards (Splunk & Elastic)
- ✅ Support for 50+ new artifact types
- ✅ Multi-cloud forensic acquisition and analysis
- ✅ Natural language querying of investigation data

---

## Feature 1: Latest MITRE ATT&CK Integration

### Current State

**Problem:**
- Static MITRE ATT&CK mappings (may be outdated)
- Manual updates required
- Dashboard templates hardcoded with specific version

**Current Location:**
- `analysis/rivendell/post/mitre/`
- Splunk app templates
- Static JSON mappings

### Proposed Solution

#### 1.1 Auto-Update Mechanism

**Module**: `analysis/mitre/attck_updater.py`

```python
class MitreAttackUpdater:
    """
    Automatically fetch and update MITRE ATT&CK framework data.

    Features:
    - Download latest ATT&CK STIX data from GitHub
    - Parse and cache locally
    - Version tracking
    - Automatic weekly updates
    - Backward compatibility with old versions
    """

    def __init__(self):
        self.source_url = "https://github.com/mitre/cti/raw/master/enterprise-attack/enterprise-attack.json"
        self.cache_dir = "/opt/rivendell/data/mitre"
        self.current_version = self.get_current_version()

    def check_for_updates(self) -> bool:
        """Check if new version available."""
        pass

    def download_latest(self) -> str:
        """Download latest ATT&CK data."""
        pass

    def parse_stix_data(self, data: dict) -> dict:
        """Parse STIX 2.0 formatted data."""
        pass

    def update_local_cache(self):
        """Update cached ATT&CK data."""
        pass
```

**Features:**
- Scheduled updates (configurable: daily/weekly/monthly)
- Version comparison
- Graceful fallback to cached version if download fails
- Notification on new techniques
- Changelog generation

#### 1.2 Dynamic Technique Mapping

**Module**: `analysis/mitre/technique_mapper.py`

```python
class TechniqueMapper:
    """
    Map forensic artifacts to ATT&CK techniques dynamically.

    Supports:
    - Automatic mapping based on artifact type
    - Custom mapping rules
    - Confidence scoring
    - Multi-technique artifacts
    """

    ARTIFACT_MAPPINGS = {
        # Windows
        'prefetch': ['T1059', 'T1106'],  # Execution techniques
        'scheduled_tasks': ['T1053.005'],
        'registry_run_keys': ['T1547.001'],
        'wmi_persistence': ['T1546.003'],

        # Linux
        'cron_jobs': ['T1053.003'],
        'systemd_services': ['T1543.002'],
        'bash_history': ['T1059.004'],

        # macOS
        'launch_agents': ['T1543.001'],
        'login_items': ['T1547.015'],
    }

    def map_artifact_to_techniques(self, artifact_type: str, artifact_data: dict) -> list:
        """Map artifact to ATT&CK techniques with confidence."""
        pass

    def get_technique_details(self, technique_id: str) -> dict:
        """Get full technique details from cache."""
        pass
```

#### 1.3 Dashboard Template Generator

**Module**: `analysis/mitre/dashboard_generator.py`

```python
class MitreDashboardGenerator:
    """
    Generate SIEM dashboard templates for latest ATT&CK version.

    Outputs:
    - Splunk dashboards (XML)
    - Elastic/Kibana dashboards (JSON)
    - HTML static reports
    - ATT&CK Navigator JSON
    """

    def generate_splunk_dashboard(self, techniques: list) -> str:
        """Generate Splunk dashboard XML."""
        pass

    def generate_elastic_dashboard(self, techniques: list) -> str:
        """Generate Kibana dashboard JSON."""
        pass

    def generate_navigator_layer(self, coverage: dict) -> dict:
        """Generate ATT&CK Navigator layer."""
        pass
```

**Template Structure:**
```
templates/mitre/
├── splunk/
│   ├── coverage_heatmap.xml
│   ├── technique_timeline.xml
│   └── tactic_overview.xml
├── elastic/
│   ├── coverage_dashboard.json
│   ├── technique_viz.json
│   └── index_pattern.json
└── navigator/
    └── coverage_layer.json
```

### Implementation Steps

1. **Week 1**: Create `MitreAttackUpdater` class
   - Implement STIX data download
   - Parse techniques, tactics, sub-techniques
   - Version tracking and caching

2. **Week 2**: Create `TechniqueMapper` class
   - Dynamic artifact-to-technique mapping
   - Confidence scoring algorithm
   - Custom mapping rules engine

3. **Week 3**: Create `MitreDashboardGenerator` class
   - Splunk dashboard templates
   - Elastic dashboard templates
   - ATT&CK Navigator layers

4. **Week 4**: Integration and testing
   - Automated update scheduling
   - Dashboard deployment automation
   - Version migration testing

### Configuration

**File**: `config/mitre.yml`

```yaml
mitre_attack:
  auto_update:
    enabled: true
    schedule: weekly  # daily, weekly, monthly
    check_time: "02:00"  # 2 AM

  source:
    primary: "https://github.com/mitre/cti"
    fallback: "https://attack.mitre.org/stix/enterprise-attack.json"

  cache:
    directory: "/opt/rivendell/data/mitre"
    retention_days: 90  # Keep old versions

  mapping:
    confidence_threshold: 0.7  # Minimum confidence for mapping
    include_deprecated: false
    include_revoked: false

  dashboards:
    splunk:
      enabled: true
      auto_deploy: true
      app_name: "rivendell_mitre"

    elastic:
      enabled: true
      auto_deploy: true
      index_pattern: "rivendell-*"

  notifications:
    enabled: true
    method: email  # email, slack, webhook
    recipients:
      - analyst@example.com
```

### Output Examples

**ATT&CK Coverage Report** (`/output/CASE-001/mitre/coverage.json`):
```json
{
  "version": "14.1",
  "generated": "2025-11-12T14:30:00Z",
  "case_id": "CASE-001",
  "coverage": {
    "tactics": {
      "initial_access": {
        "techniques_found": 3,
        "techniques_total": 9,
        "coverage_percent": 33.3
      },
      "execution": {
        "techniques_found": 12,
        "techniques_total": 13,
        "coverage_percent": 92.3
      }
    },
    "techniques": [
      {
        "id": "T1059.001",
        "name": "PowerShell",
        "tactic": ["execution"],
        "confidence": 0.95,
        "evidence": [
          "/output/processed/powershell_history.csv",
          "/output/processed/prefetch/powershell.exe.pf"
        ],
        "count": 47
      }
    ]
  }
}
```

---

## Feature 2: Standalone MITRE Coverage Analysis

### Current State

**Problem:**
- Requires full SIEM data ingestion before coverage analysis
- No real-time coverage during analysis
- Cannot generate coverage report without SIEM

**Current Workflow:**
1. Analyze evidence with Elrond
2. Export to Splunk/Elastic
3. Wait for indexing
4. Run Splunk queries
5. Generate dashboard

### Proposed Solution

#### 2.1 Real-Time Coverage Analyzer

**Module**: `analysis/mitre/coverage_analyzer.py`

```python
class MitreCoverageAnalyzer:
    """
    Generate ATT&CK coverage during analysis phase.

    Features:
    - Real-time technique detection
    - No SIEM dependency
    - Standalone HTML reports
    - JSON export for dashboards
    - Progressive coverage updates
    """

    def __init__(self, case_id: str, output_dir: str):
        self.case_id = case_id
        self.output_dir = output_dir
        self.coverage = {
            'tactics': {},
            'techniques': {},
            'sub_techniques': {}
        }
        self.evidence_tracker = {}

    def analyze_artifact(self, artifact_type: str, artifact_path: str, data: dict):
        """
        Analyze single artifact and update coverage.

        Args:
            artifact_type: Type of artifact (e.g., 'prefetch', 'registry')
            artifact_path: Path to artifact file
            data: Parsed artifact data
        """
        techniques = self.mapper.map_artifact_to_techniques(artifact_type, data)

        for technique in techniques:
            self.add_technique_evidence(
                technique['id'],
                technique['confidence'],
                artifact_path,
                technique.get('details', {})
            )

    def add_technique_evidence(self, technique_id: str, confidence: float,
                               evidence_path: str, details: dict):
        """Add evidence for a technique."""
        if technique_id not in self.coverage['techniques']:
            self.coverage['techniques'][technique_id] = {
                'evidence': [],
                'confidence_max': 0.0,
                'count': 0
            }

        self.coverage['techniques'][technique_id]['evidence'].append({
            'path': evidence_path,
            'confidence': confidence,
            'details': details
        })
        self.coverage['techniques'][technique_id]['count'] += 1
        self.coverage['techniques'][technique_id]['confidence_max'] = max(
            self.coverage['techniques'][technique_id]['confidence_max'],
            confidence
        )

    def generate_coverage_report(self) -> dict:
        """Generate comprehensive coverage report."""
        pass

    def export_html_report(self, output_path: str):
        """Export standalone HTML report."""
        pass

    def export_navigator_json(self, output_path: str):
        """Export ATT&CK Navigator JSON."""
        pass

    def export_for_siem(self, siem_type: str) -> str:
        """Export coverage data for SIEM ingestion."""
        pass
```

#### 2.2 Integration with Elrond Analysis

**Modified**: `analysis/rivendell/process/process.py`

```python
# Add coverage analyzer to processing pipeline

from analysis.mitre.coverage_analyzer import MitreCoverageAnalyzer

class Processor:
    def __init__(self, case_id, output_dir):
        self.case_id = case_id
        self.coverage = MitreCoverageAnalyzer(case_id, output_dir)

    def process_artifact(self, artifact_type, artifact_path):
        # Existing processing logic
        data = self.parse_artifact(artifact_type, artifact_path)

        # NEW: Real-time coverage analysis
        self.coverage.analyze_artifact(artifact_type, artifact_path, data)

        # Save processed data
        self.save_processed_data(data)

    def finalize(self):
        # Generate final coverage report
        report = self.coverage.generate_coverage_report()

        # Export multiple formats
        self.coverage.export_html_report(f"{self.output_dir}/mitre/coverage.html")
        self.coverage.export_navigator_json(f"{self.output_dir}/mitre/navigator.json")

        # Export for SIEM ingestion
        splunk_data = self.coverage.export_for_siem('splunk')
        elastic_data = self.coverage.export_for_siem('elastic')
```

#### 2.3 Standalone Dashboard Generator

**Module**: `analysis/mitre/standalone_dashboard.py`

```python
class StandaloneDashboard:
    """
    Generate interactive HTML dashboard without SIEM.

    Features:
    - ATT&CK matrix heatmap
    - Technique timeline
    - Evidence browser
    - Search and filter
    - Export capabilities
    """

    def generate_html(self, coverage_data: dict) -> str:
        """Generate complete HTML dashboard."""
        template = self.load_template('dashboard.html')

        # Inject data and JavaScript
        html = template.format(
            coverage_json=json.dumps(coverage_data),
            matrix_html=self.generate_matrix_html(coverage_data),
            timeline_html=self.generate_timeline_html(coverage_data),
            evidence_html=self.generate_evidence_browser(coverage_data)
        )

        return html
```

**Dashboard Features:**
- **Interactive Matrix**: Click techniques to see evidence
- **Coverage Heatmap**: Color-coded by detection count
- **Timeline View**: When techniques were detected
- **Evidence Browser**: List all supporting evidence
- **Search**: Find techniques by name, tactic, or ID
- **Export**: JSON, CSV, PDF reports
- **Offline**: No server required, single HTML file

#### 2.4 SIEM Integration

**Module**: `analysis/mitre/siem_integration.py`

```python
class MitreSiemIntegration:
    """
    Push coverage data to SIEM platforms.

    Features:
    - Pre-computed coverage metrics
    - Optimized queries
    - Dashboard auto-creation
    - Real-time updates
    """

    def push_to_splunk(self, coverage_data: dict, splunk_config: dict):
        """Push coverage data to Splunk HEC."""
        # Convert coverage to Splunk events
        events = self.format_for_splunk(coverage_data)

        # Push via HEC
        self.splunk_client.send_events(events)

        # Deploy dashboard
        self.deploy_splunk_dashboard(coverage_data['techniques'])

    def push_to_elastic(self, coverage_data: dict, elastic_config: dict):
        """Push coverage data to Elasticsearch."""
        # Convert to Elasticsearch documents
        docs = self.format_for_elastic(coverage_data)

        # Bulk index
        self.elastic_client.bulk_index(docs)

        # Deploy Kibana dashboard
        self.deploy_kibana_dashboard(coverage_data['techniques'])
```

### Implementation Steps

1. **Week 1**: Create `MitreCoverageAnalyzer`
   - Real-time technique detection
   - Evidence tracking
   - Coverage calculation

2. **Week 2**: Integrate with Elrond pipeline
   - Modify processors to call coverage analyzer
   - Add coverage hooks to all artifact parsers
   - Generate reports during analysis

3. **Week 3**: Create standalone dashboard
   - HTML template with embedded JavaScript
   - Interactive ATT&CK matrix
   - Evidence browser

4. **Week 4**: SIEM integration
   - Splunk HEC push with pre-computed metrics
   - Elasticsearch bulk index
   - Dashboard auto-deployment

### Output Structure

```
/output/CASE-001/
├── mitre/
│   ├── coverage.json           # Raw coverage data
│   ├── coverage.html           # Standalone dashboard
│   ├── navigator.json          # ATT&CK Navigator layer
│   ├── techniques.csv          # Technique list with evidence
│   ├── tactics_summary.csv     # Tactic coverage summary
│   ├── evidence_map.json       # Artifact-to-technique mapping
│   └── dashboards/
│       ├── splunk_dashboard.xml
│       └── kibana_dashboard.json
```

### Benefits

✅ **No SIEM Required**: Generate coverage during analysis
✅ **Real-Time**: See coverage as artifacts are processed
✅ **Offline Reports**: Standalone HTML dashboard
✅ **SIEM Ready**: Pre-computed data for instant dashboards
✅ **Multi-Format**: JSON, HTML, CSV, Navigator

---

## Feature 3: Enhanced Artifact Parsing

### 3.1 WMI Artifact Parsing (Windows)

#### Current Gap

**Missing WMI Artifacts:**
- WMI Event Consumers (persistence)
- WMI Event Filters (triggers)
- WMI Event Bindings (linking)
- WMI Namespaces
- WMI Class modifications
- WMI Query history

#### Implementation

**Module**: `analysis/rivendell/process/extractions/wmi_full.py`

```python
class WmiArtifactParser:
    """
    Comprehensive WMI artifact parser.

    Parses:
    - Event Consumers (ActiveScriptEventConsumer, CommandLineEventConsumer, etc.)
    - Event Filters
    - Filter-to-Consumer Bindings
    - WMI Namespaces
    - WMI Repository (OBJECTS.DATA)
    - MOF files
    """

    WMI_REPOSITORY_PATHS = [
        "Windows/System32/wbem/Repository/",
        "Windows/System32/wbem/Repository/FS/",
    ]

    def parse_wmi_repository(self, mount_point: str) -> list:
        """
        Parse WMI repository files.

        Files:
        - OBJECTS.DATA: Main WMI object store
        - INDEX.BTR: Index file
        - MAPPING*.MAP: Namespace mappings
        """
        artifacts = []

        for repo_path in self.WMI_REPOSITORY_PATHS:
            full_path = os.path.join(mount_point, repo_path)

            # Parse OBJECTS.DATA
            objects_file = os.path.join(full_path, "OBJECTS.DATA")
            if os.path.exists(objects_file):
                objects = self.parse_objects_data(objects_file)
                artifacts.extend(objects)

        return artifacts

    def parse_objects_data(self, file_path: str) -> list:
        """Parse OBJECTS.DATA file for WMI objects."""
        # Use python-cim or custom parser
        pass

    def extract_event_consumers(self, objects: list) -> list:
        """Extract WMI Event Consumers."""
        consumers = []

        for obj in objects:
            if obj.get('__CLASS') in [
                'ActiveScriptEventConsumer',
                'CommandLineEventConsumer',
                'LogFileEventConsumer',
                'NTEventLogEventConsumer',
                'SMTPEventConsumer'
            ]:
                consumer = {
                    'type': obj['__CLASS'],
                    'name': obj.get('Name'),
                    'creation_time': obj.get('CreatorSID'),
                    'script_text': obj.get('ScriptText'),  # ActiveScript
                    'command_line': obj.get('CommandLineTemplate'),  # CommandLine
                    'attck_techniques': ['T1546.003']  # WMI Event Subscription
                }
                consumers.append(consumer)

        return consumers

    def extract_event_filters(self, objects: list) -> list:
        """Extract WMI Event Filters."""
        filters = []

        for obj in objects:
            if obj.get('__CLASS') == '__EventFilter':
                filter_obj = {
                    'name': obj.get('Name'),
                    'query': obj.get('Query'),
                    'query_language': obj.get('QueryLanguage'),
                    'event_namespace': obj.get('EventNamespace'),
                    'attck_techniques': ['T1546.003']
                }
                filters.append(filter_obj)

        return filters

    def extract_bindings(self, objects: list) -> list:
        """Extract Filter-to-Consumer bindings."""
        bindings = []

        for obj in objects:
            if obj.get('__CLASS') == '__FilterToConsumerBinding':
                binding = {
                    'filter': obj.get('Filter'),
                    'consumer': obj.get('Consumer'),
                    'attck_techniques': ['T1546.003']
                }
                bindings.append(binding)

        return bindings
```

**Collection via Gandalf**:

```python
# acquisition/python/collect_artefacts-py
# Add WMI repository to collection paths

WMI_ARTIFACTS = [
    "Windows/System32/wbem/Repository/OBJECTS.DATA",
    "Windows/System32/wbem/Repository/INDEX.BTR",
    "Windows/System32/wbem/Repository/MAPPING*.MAP",
    "Windows/System32/wbem/Repository/FS/OBJECTS.DATA",
    "Windows/System32/wbem/MOF/",
]
```

#### ATT&CK Mapping

WMI artifacts map to:
- **T1546.003**: Event Triggered Execution - Windows Management Instrumentation Event Subscription
- **T1047**: Windows Management Instrumentation
- **T1059.001**: PowerShell (often used with WMI)
- **T1569.002**: Service Execution (WMI can start services)

### 3.2 Enhanced macOS Artifacts

#### New Artifacts to Collect

**Module**: `acquisition/models/macos_artifacts.py`

```python
MACOS_ARTIFACTS_EXTENDED = {
    # Existing + New
    "/.fseventsd/": "fseventsd",                    # File system events
    "/Library/Logs/DiagnosticReports/": "crash_reports",
    "/var/log/system.log": "system_log",
    "/var/log/install.log": "install_log",

    # NEW: Unified Logging
    "/private/var/db/diagnostics/": "unified_logs",
    "/private/var/db/uuidtext/": "unified_logs",

    # NEW: Application Usage
    "/var/db/CoreDuet/": "coreduet",                # App usage tracking
    "/Library/Application Support/com.apple.TCC/": "tcc",  # Privacy permissions

    # NEW: Network
    "/Library/Preferences/SystemConfiguration/": "network_config",
    "/private/var/db/dhcpclient/": "dhcp_leases",

    # NEW: Browser Extensions
    "/Users/*/Library/Safari/Extensions/": "safari_extensions",
    "/Users/*/Library/Application Support/Google/Chrome/Default/Extensions/": "chrome_extensions",

    # NEW: Spotlight
    "/.Spotlight-V100/": "spotlight",
    "/Users/*/.Spotlight-V100/": "spotlight",

    # NEW: Time Machine
    "/private/var/db/.TimeMachine/": "timemachine",

    # NEW: FileVault
    "/var/db/FileVaultKeys/": "filevault",

    # NEW: Keychain
    "/Users/*/Library/Keychains/": "keychains",
    "/Library/Keychains/": "keychains",

    # NEW: Quarantine
    "/Users/*/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2": "quarantine",
}
```

**New Parsers**:

1. **Unified Log Parser** (`analysis/rivendell/process/extractions/macos/unified_log.py`):
   ```python
   class UnifiedLogParser:
       """Parse macOS Unified Logging (tracev3 files)."""

       def parse_tracev3(self, file_path: str) -> list:
           """Parse tracev3 unified log format."""
           # Use UnifiedLogReader or custom parser
           pass
   ```

2. **CoreDuet Parser** (`analysis/rivendell/process/extractions/macos/coreduet.py`):
   ```python
   class CoreDuetParser:
       """Parse CoreDuet application usage database."""

       def parse_knowledge_db(self, db_path: str) -> list:
           """Parse knowledge-c.db for app usage patterns."""
           # SQLite database with app launches, focus time, etc.
           pass
   ```

3. **TCC Parser** (`analysis/rivendell/process/extractions/macos/tcc.py`):
   ```python
   class TCCParser:
       """Parse TCC.db (Transparency, Consent, and Control)."""

       def parse_tcc_db(self, db_path: str) -> list:
           """Parse TCC.db for privacy permissions."""
           # Which apps have access to camera, microphone, files, etc.
           pass
   ```

4. **FSEvents Parser** (`analysis/rivendell/process/extractions/macos/fseventsd.py`):
   ```python
   class FSEventsParser:
       """Parse FSEvents logs for file system activity."""

       def parse_fseventsd(self, fseventsd_dir: str) -> list:
           """Parse FSEvents for file modifications."""
           # Track file creates, modifies, deletes
           pass
   ```

### 3.3 Enhanced Linux Artifacts

#### New Artifacts to Collect

**Module**: `acquisition/models/linux_artifacts.py`

```python
LINUX_ARTIFACTS_EXTENDED = {
    # Existing + New

    # NEW: Systemd Journal
    "/var/log/journal/": "journal",
    "/run/log/journal/": "journal",

    # NEW: Audit Logs
    "/var/log/audit/": "audit",

    # NEW: Command History (all users)
    "/home/*/.bash_history": "bash_history",
    "/home/*/.zsh_history": "zsh_history",
    "/home/*/.python_history": "python_history",
    "/root/.bash_history": "bash_history",

    # NEW: SSH
    "/home/*/.ssh/": "ssh_keys",
    "/root/.ssh/": "ssh_keys",
    "/etc/ssh/": "ssh_config",
    "/var/log/auth.log": "auth_log",

    # NEW: Docker/Containers
    "/var/lib/docker/containers/": "docker_containers",
    "/var/lib/docker/volumes/": "docker_volumes",
    "/var/log/docker.log": "docker_log",

    # NEW: Package Management
    "/var/log/dpkg.log": "package_log",        # Debian/Ubuntu
    "/var/log/apt/": "package_log",
    "/var/log/yum.log": "package_log",         # RHEL/CentOS

    # NEW: Network Connections
    "/proc/net/tcp": "network_connections",
    "/proc/net/udp": "network_connections",
    "/proc/net/unix": "network_sockets",

    # NEW: Loaded Modules
    "/proc/modules": "kernel_modules",
    "/sys/module/": "kernel_modules",

    # NEW: Process Information
    "/proc/*/cmdline": "process_cmdline",
    "/proc/*/environ": "process_environ",
    "/proc/*/maps": "process_maps",

    # NEW: User Activity
    "/var/log/wtmp": "login_records",
    "/var/log/btmp": "failed_logins",
    "/var/log/lastlog": "last_login",

    # NEW: Scheduled Tasks
    "/var/spool/cron/": "cron_jobs",
    "/etc/cron.d/": "cron_jobs",
    "/etc/cron.hourly/": "cron_jobs",

    # NEW: X11/Wayland
    "/home/*/.xsession-errors": "x11_errors",
    "/home/*/.local/share/xorg/": "x11_logs",
}
```

**New Parsers**:

1. **Systemd Journal Parser** (`analysis/rivendell/process/extractions/linux/journal.py`):
   ```python
   class SystemdJournalParser:
       """Parse systemd binary journal files."""

       def parse_journal(self, journal_path: str) -> list:
           """Parse binary journal files."""
           # Use systemd-python or custom parser
           pass
   ```

2. **Auditd Parser** (`analysis/rivendell/process/extractions/linux/auditd.py`):
   ```python
   class AuditdParser:
       """Parse Linux audit daemon logs."""

       def parse_audit_log(self, log_path: str) -> list:
           """Parse audit.log for security events."""
           # Syscall auditing, file access, user actions
           pass
   ```

3. **Docker Forensics** (`analysis/rivendell/process/extractions/linux/docker.py`):
   ```python
   class DockerForensics:
       """Analyze Docker container artifacts."""

       def parse_container_logs(self, container_dir: str) -> list:
           """Parse Docker container logs and metadata."""
           pass

       def extract_container_filesystem(self, container_id: str) -> str:
           """Extract container filesystem for analysis."""
           pass
   ```

### Implementation Steps

**Week 1-2**: WMI Parsing
- Implement WMI repository parser
- Add WMI collectors to Gandalf
- Create WMI-specific ATT&CK mappings

**Week 3-4**: macOS Enhancements
- Implement unified log parser
- Add CoreDuet, TCC, FSEvents parsers
- Update Gandalf collection paths

**Week 5-6**: Linux Enhancements
- Implement systemd journal parser
- Add auditd and Docker parsers
- Update collection paths

---

## Feature 4: Cloud Forensics Support

### 4.1 Overview

**Supported Cloud Providers:**
- Amazon Web Services (AWS)
- Microsoft Azure
- Google Cloud Platform (GCP)

**Artifact Types:**
- VM disk images
- Cloud storage snapshots
- API/CloudTrail logs
- Container images
- Serverless function logs
- Database dumps

### 4.2 Architecture

**New Module Structure:**
```
rivendell/
├── cloud/
│   ├── __init__.py
│   ├── base.py                 # Base cloud provider class
│   ├── aws/
│   │   ├── __init__.py
│   │   ├── ec2.py             # EC2 instance forensics
│   │   ├── s3.py              # S3 bucket analysis
│   │   ├── cloudtrail.py      # CloudTrail log analysis
│   │   ├── lambda_func.py     # Lambda function forensics
│   │   └── rds.py             # RDS snapshot analysis
│   ├── azure/
│   │   ├── __init__.py
│   │   ├── vm.py              # Virtual machine forensics
│   │   ├── blob.py            # Blob storage analysis
│   │   ├── activity_log.py    # Activity log analysis
│   │   └── functions.py       # Azure Functions forensics
│   ├── gcp/
│   │   ├── __init__.py
│   │   ├── compute.py         # Compute Engine forensics
│   │   ├── storage.py         # Cloud Storage analysis
│   │   ├── logging.py         # Cloud Logging analysis
│   │   └── functions.py       # Cloud Functions forensics
│   └── acquisition/
│       ├── aws_acquire.py
│       ├── azure_acquire.py
│       └── gcp_acquire.py
```

### 4.3 Implementation

#### Base Cloud Provider Class

**Module**: `cloud/base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class CloudProvider(ABC):
    """Base class for cloud provider forensics."""

    def __init__(self, credentials: Dict):
        self.credentials = credentials
        self.client = None

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with cloud provider."""
        pass

    @abstractmethod
    def list_instances(self, region: str = None) -> List[Dict]:
        """List all compute instances."""
        pass

    @abstractmethod
    def acquire_disk_image(self, instance_id: str, output_dir: str) -> str:
        """Acquire disk image from instance."""
        pass

    @abstractmethod
    def acquire_logs(self, start_time: str, end_time: str, output_dir: str) -> List[str]:
        """Acquire cloud audit/activity logs."""
        pass

    @abstractmethod
    def acquire_storage(self, bucket_name: str, output_dir: str) -> str:
        """Acquire cloud storage artifacts."""
        pass
```

#### AWS Implementation

**Module**: `cloud/aws/ec2.py`

```python
import boto3
from datetime import datetime
from ..base import CloudProvider

class AWSForensics(CloudProvider):
    """AWS forensics acquisition and analysis."""

    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.session = None

    def authenticate(self) -> bool:
        """Authenticate with AWS using credentials."""
        try:
            self.session = boto3.Session(
                aws_access_key_id=self.credentials['access_key'],
                aws_secret_access_key=self.credentials['secret_key'],
                region_name=self.credentials.get('region', 'us-east-1')
            )
            # Test credentials
            sts = self.session.client('sts')
            sts.get_caller_identity()
            return True
        except Exception as e:
            raise Exception(f"AWS authentication failed: {e}")

    def list_instances(self, region: str = None) -> List[Dict]:
        """List all EC2 instances."""
        ec2 = self.session.client('ec2', region_name=region)
        response = ec2.describe_instances()

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'id': instance['InstanceId'],
                    'type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'launch_time': instance['LaunchTime'],
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                })

        return instances

    def acquire_disk_image(self, instance_id: str, output_dir: str) -> str:
        """
        Acquire EBS volume snapshot and export.

        Steps:
        1. Identify attached EBS volumes
        2. Create snapshots
        3. Export to S3 (optional)
        4. Download as raw disk image
        """
        ec2 = self.session.client('ec2')

        # Get instance details
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        # Get attached volumes
        volumes = [
            mapping['Ebs']['VolumeId']
            for mapping in instance['BlockDeviceMappings']
        ]

        snapshots = []
        for volume_id in volumes:
            # Create snapshot
            snapshot = ec2.create_snapshot(
                VolumeId=volume_id,
                Description=f'Forensic snapshot of {instance_id} - {datetime.now()}'
            )
            snapshots.append(snapshot['SnapshotId'])

            # Wait for snapshot to complete
            waiter = ec2.get_waiter('snapshot_completed')
            waiter.wait(SnapshotIds=[snapshot['SnapshotId']])

        # Export snapshots (implementation depends on requirements)
        # Option 1: Export to S3 then download
        # Option 2: Create volume from snapshot and dd

        return snapshots

    def acquire_cloudtrail_logs(self, start_time: str, end_time: str,
                                 output_dir: str) -> List[str]:
        """Acquire CloudTrail logs for timeframe."""
        cloudtrail = self.session.client('cloudtrail')

        logs = []
        paginator = cloudtrail.get_paginator('lookup_events')

        for page in paginator.paginate(
            StartTime=start_time,
            EndTime=end_time
        ):
            for event in page['Events']:
                logs.append({
                    'event_time': event['EventTime'],
                    'event_name': event['EventName'],
                    'username': event.get('Username'),
                    'resources': event.get('Resources', []),
                    'cloud_trail_event': event['CloudTrailEvent']
                })

        # Save to file
        output_file = f"{output_dir}/cloudtrail_{start_time}_{end_time}.json"
        with open(output_file, 'w') as f:
            json.dump(logs, f, indent=2, default=str)

        return [output_file]

    def analyze_s3_bucket(self, bucket_name: str, output_dir: str) -> Dict:
        """Analyze S3 bucket for forensic artifacts."""
        s3 = self.session.client('s3')

        # Get bucket logging configuration
        try:
            logging = s3.get_bucket_logging(Bucket=bucket_name)
        except:
            logging = None

        # Get bucket versioning
        try:
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        except:
            versioning = None

        # List objects with metadata
        objects = []
        paginator = s3.get_paginator('list_object_versions')
        for page in paginator.paginate(Bucket=bucket_name):
            for version in page.get('Versions', []):
                objects.append({
                    'key': version['Key'],
                    'version_id': version['VersionId'],
                    'last_modified': version['LastModified'],
                    'size': version['Size'],
                    'etag': version['ETag']
                })

        return {
            'bucket': bucket_name,
            'logging': logging,
            'versioning': versioning,
            'objects': objects
        }
```

**Module**: `cloud/aws/cloudtrail.py`

```python
class CloudTrailAnalyzer:
    """Analyze CloudTrail logs for suspicious activity."""

    SUSPICIOUS_EVENTS = [
        'DeleteTrail',
        'StopLogging',
        'UpdateTrail',
        'PutBucketLogging',
        'DeleteBucket',
        'CreateAccessKey',
        'RunInstances',
        'AuthorizeSecurityGroupIngress',
    ]

    def analyze_logs(self, log_file: str) -> Dict:
        """Analyze CloudTrail logs for suspicious activity."""
        with open(log_file, 'r') as f:
            logs = json.load(f)

        findings = {
            'suspicious_events': [],
            'unusual_sources': [],
            'privilege_escalations': [],
            'data_exfiltration': []
        }

        for event in logs:
            # Check for suspicious event names
            if event['event_name'] in self.SUSPICIOUS_EVENTS:
                findings['suspicious_events'].append(event)

            # Check for unusual source IPs
            if self.is_unusual_source(event):
                findings['unusual_sources'].append(event)

            # Check for privilege escalation
            if self.is_privilege_escalation(event):
                findings['privilege_escalations'].append(event)

        return findings

    def map_to_mitre(self, findings: Dict) -> Dict:
        """Map CloudTrail findings to MITRE ATT&CK."""
        mappings = {
            'DeleteTrail': ['T1070.003'],  # Clear Cloud Logs
            'StopLogging': ['T1070.003'],
            'CreateAccessKey': ['T1098'],  # Account Manipulation
            'RunInstances': ['T1578.002'], # Create Cloud Instance
        }

        techniques = {}
        for event in findings['suspicious_events']:
            event_name = event['event_name']
            if event_name in mappings:
                for technique in mappings[event_name]:
                    if technique not in techniques:
                        techniques[technique] = []
                    techniques[technique].append(event)

        return techniques
```

#### Azure Implementation

**Module**: `cloud/azure/vm.py`

```python
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient

class AzureForensics(CloudProvider):
    """Azure forensics acquisition and analysis."""

    def authenticate(self) -> bool:
        """Authenticate with Azure using service principal."""
        try:
            self.credential = ClientSecretCredential(
                tenant_id=self.credentials['tenant_id'],
                client_id=self.credentials['client_id'],
                client_secret=self.credentials['client_secret']
            )

            self.compute_client = ComputeManagementClient(
                self.credential,
                self.credentials['subscription_id']
            )

            return True
        except Exception as e:
            raise Exception(f"Azure authentication failed: {e}")

    def list_instances(self, resource_group: str = None) -> List[Dict]:
        """List all Azure VMs."""
        vms = []

        if resource_group:
            vm_list = self.compute_client.virtual_machines.list(resource_group)
        else:
            vm_list = self.compute_client.virtual_machines.list_all()

        for vm in vm_list:
            vms.append({
                'id': vm.id,
                'name': vm.name,
                'location': vm.location,
                'vm_size': vm.hardware_profile.vm_size,
                'os_type': vm.storage_profile.os_disk.os_type,
                'tags': vm.tags
            })

        return vms

    def acquire_disk_snapshot(self, vm_name: str, resource_group: str,
                              output_dir: str) -> str:
        """Create and export VM disk snapshot."""
        from azure.mgmt.compute.models import Snapshot, CreationData

        # Get VM
        vm = self.compute_client.virtual_machines.get(resource_group, vm_name)

        # Get OS disk
        os_disk = vm.storage_profile.os_disk

        # Create snapshot
        snapshot_name = f"{vm_name}-snapshot-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        snapshot = Snapshot(
            location=vm.location,
            creation_data=CreationData(
                create_option='Copy',
                source_uri=os_disk.managed_disk.id
            )
        )

        async_snapshot = self.compute_client.snapshots.begin_create_or_update(
            resource_group,
            snapshot_name,
            snapshot
        )

        snapshot_resource = async_snapshot.result()

        return snapshot_resource.id

    def acquire_activity_logs(self, start_time: str, end_time: str,
                              output_dir: str) -> List[str]:
        """Acquire Azure Activity Logs."""
        monitor_client = MonitorManagementClient(
            self.credential,
            self.credentials['subscription_id']
        )

        logs = []
        activity_logs = monitor_client.activity_logs.list(
            filter=f"eventTimestamp ge '{start_time}' and eventTimestamp le '{end_time}'"
        )

        for log in activity_logs:
            logs.append({
                'timestamp': log.event_timestamp,
                'operation_name': log.operation_name.value,
                'caller': log.caller,
                'resource_id': log.resource_id,
                'status': log.status.value
            })

        # Save to file
        output_file = f"{output_dir}/azure_activity_logs_{start_time}_{end_time}.json"
        with open(output_file, 'w') as f:
            json.dump(logs, f, indent=2, default=str)

        return [output_file]
```

#### GCP Implementation

**Module**: `cloud/gcp/compute.py`

```python
from google.cloud import compute_v1
from google.cloud import logging_v2

class GCPForensics(CloudProvider):
    """GCP forensics acquisition and analysis."""

    def authenticate(self) -> bool:
        """Authenticate with GCP using service account."""
        import os

        # Set credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials['service_account_file']

        try:
            self.compute_client = compute_v1.InstancesClient()
            return True
        except Exception as e:
            raise Exception(f"GCP authentication failed: {e}")

    def list_instances(self, project: str, zone: str = None) -> List[Dict]:
        """List all GCE instances."""
        instances = []

        if zone:
            zones = [zone]
        else:
            zones_client = compute_v1.ZonesClient()
            zones = [z.name for z in zones_client.list(project=project)]

        for zone_name in zones:
            instance_list = self.compute_client.list(project=project, zone=zone_name)

            for instance in instance_list:
                instances.append({
                    'id': instance.id,
                    'name': instance.name,
                    'zone': zone_name,
                    'machine_type': instance.machine_type,
                    'status': instance.status,
                    'disks': [disk.source for disk in instance.disks]
                })

        return instances

    def acquire_disk_snapshot(self, instance_name: str, project: str,
                              zone: str, output_dir: str) -> str:
        """Create GCE disk snapshot."""
        # Get instance
        instance = self.compute_client.get(
            project=project,
            zone=zone,
            instance=instance_name
        )

        # Get boot disk
        boot_disk = instance.disks[0]
        disk_name = boot_disk.source.split('/')[-1]

        # Create snapshot
        disks_client = compute_v1.DisksClient()
        snapshot_name = f"{instance_name}-snapshot-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        operation = disks_client.create_snapshot(
            project=project,
            zone=zone,
            disk=disk_name,
            snapshot_resource=compute_v1.Snapshot(name=snapshot_name)
        )

        # Wait for operation to complete
        operation.result()

        return snapshot_name

    def acquire_cloud_logging(self, project: str, start_time: str,
                              end_time: str, output_dir: str) -> List[str]:
        """Acquire GCP Cloud Logging entries."""
        logging_client = logging_v2.Client(project=project)

        filter_str = f'timestamp>="{start_time}" AND timestamp<="{end_time}"'

        logs = []
        for entry in logging_client.list_entries(filter_=filter_str):
            logs.append({
                'timestamp': entry.timestamp,
                'severity': entry.severity,
                'log_name': entry.log_name,
                'resource': entry.resource,
                'payload': entry.payload
            })

        # Save to file
        output_file = f"{output_dir}/gcp_logs_{start_time}_{end_time}.json"
        with open(output_file, 'w') as f:
            json.dump(logs, f, indent=2, default=str)

        return [output_file]
```

### 4.4 Unified Cloud CLI

**Module**: `cli/cloud.py`

```python
#!/usr/bin/env python3
"""
Rivendell Cloud Forensics CLI

Usage:
    rivendell cloud acquire aws --instance-id i-1234567890 --output /evidence
    rivendell cloud acquire azure --vm-name web-server --resource-group prod
    rivendell cloud acquire gcp --instance-name app-server --project my-project

    rivendell cloud analyze aws-cloudtrail --logs /evidence/cloudtrail.json
    rivendell cloud analyze azure-activity --logs /evidence/activity.json
"""

import argparse
from cloud.aws.ec2 import AWSForensics
from cloud.azure.vm import AzureForensics
from cloud.gcp.compute import GCPForensics

def acquire_aws(args):
    """Acquire AWS forensic artifacts."""
    aws = AWSForensics(credentials={
        'access_key': args.access_key,
        'secret_key': args.secret_key,
        'region': args.region
    })

    aws.authenticate()

    if args.instance_id:
        print(f"[*] Acquiring disk image from {args.instance_id}")
        snapshots = aws.acquire_disk_image(args.instance_id, args.output)
        print(f"[+] Created snapshots: {snapshots}")

    if args.cloudtrail:
        print(f"[*] Acquiring CloudTrail logs")
        logs = aws.acquire_cloudtrail_logs(args.start_time, args.end_time, args.output)
        print(f"[+] Saved logs: {logs}")

def main():
    parser = argparse.ArgumentParser(description="Rivendell Cloud Forensics")
    subparsers = parser.add_subparsers(dest='command')

    # Acquire command
    acquire_parser = subparsers.add_parser('acquire', help='Acquire cloud artifacts')
    acquire_subparsers = acquire_parser.add_subparsers(dest='provider')

    # AWS
    aws_parser = acquire_subparsers.add_parser('aws')
    aws_parser.add_argument('--instance-id', help='EC2 instance ID')
    aws_parser.add_argument('--cloudtrail', action='store_true')
    aws_parser.add_argument('--access-key', required=True)
    aws_parser.add_argument('--secret-key', required=True)
    aws_parser.add_argument('--region', default='us-east-1')
    aws_parser.add_argument('--output', required=True)

    # Azure
    azure_parser = acquire_subparsers.add_parser('azure')
    azure_parser.add_argument('--vm-name', help='VM name')
    azure_parser.add_argument('--resource-group', required=True)
    azure_parser.add_argument('--tenant-id', required=True)
    azure_parser.add_argument('--client-id', required=True)
    azure_parser.add_argument('--client-secret', required=True)
    azure_parser.add_argument('--subscription-id', required=True)
    azure_parser.add_argument('--output', required=True)

    # GCP
    gcp_parser = acquire_subparsers.add_parser('gcp')
    gcp_parser.add_argument('--instance-name', help='Instance name')
    gcp_parser.add_argument('--project', required=True)
    gcp_parser.add_argument('--zone', required=True)
    gcp_parser.add_argument('--service-account', required=True)
    gcp_parser.add_argument('--output', required=True)

    args = parser.parse_args()

    if args.command == 'acquire':
        if args.provider == 'aws':
            acquire_aws(args)
        elif args.provider == 'azure':
            acquire_azure(args)
        elif args.provider == 'gcp':
            acquire_gcp(args)

if __name__ == '__main__':
    main()
```

### 4.5 Configuration

**File**: `config/cloud.yml`

```yaml
cloud_forensics:
  enabled: true

  aws:
    enabled: true
    regions:
      - us-east-1
      - us-west-2
      - eu-west-1

    artifacts:
      - ec2_instances
      - ebs_snapshots
      - cloudtrail_logs
      - s3_buckets
      - lambda_functions
      - rds_snapshots

    retention:
      snapshots_days: 30
      logs_days: 90

  azure:
    enabled: true
    regions:
      - eastus
      - westus2
      - northeurope

    artifacts:
      - virtual_machines
      - disk_snapshots
      - activity_logs
      - blob_storage
      - azure_functions

  gcp:
    enabled: true
    regions:
      - us-central1
      - us-east1
      - europe-west1

    artifacts:
      - compute_instances
      - persistent_disks
      - cloud_logging
      - cloud_storage
      - cloud_functions

  mitre_mapping:
    cloud_techniques:
      - T1078.004  # Cloud Accounts
      - T1530      # Data from Cloud Storage
      - T1537      # Transfer Data to Cloud Account
      - T1578      # Modify Cloud Compute Infrastructure
      - T1580      # Cloud Infrastructure Discovery
      - T1619      # Cloud Storage Object Discovery
```

### Implementation Steps

**Week 1-2**: AWS Support
- Implement EC2 disk acquisition
- CloudTrail log collection
- S3 bucket analysis

**Week 3-4**: Azure Support
- Implement VM disk snapshots
- Activity log collection
- Blob storage analysis

**Week 5-6**: GCP Support
- Implement GCE disk snapshots
- Cloud Logging collection
- Cloud Storage analysis

**Week 7**: Integration
- Unified CLI
- MITRE ATT&CK cloud techniques mapping
- Documentation

---

## Feature 5: AI-Powered Analysis Agent

### 5.1 Overview

**Goal**: Enable analysts to query investigation data using natural language.

**Capabilities:**
- Query forensic artifacts using natural language
- Answer questions about timeline events
- Identify relationships between artifacts
- Suggest investigation paths
- Generate summaries and reports

### 5.2 Architecture

**Components:**
1. **Local LLM**: Privacy-focused, on-premises AI model
2. **Vector Database**: Efficient similarity search
3. **Query Interface**: Web UI and CLI
4. **Context Builder**: Prepare relevant data for LLM

**Technology Stack:**
- **LLM**: Llama 3 70B or Mistral Large (local deployment)
- **Vector DB**: ChromaDB or Qdrant
- **Embedding Model**: all-MiniLM-L6-v2
- **Framework**: LangChain for orchestration

### 5.3 Implementation

#### Data Indexing

**Module**: `ai/indexer.py`

```python
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ForensicDataIndexer:
    """
    Index forensic artifacts for AI querying.

    Indexes:
    - Timeline events
    - Artifact metadata
    - IOCs
    - Process lists
    - Network connections
    - File listings
    """

    def __init__(self, case_id: str, output_dir: str):
        self.case_id = case_id
        self.output_dir = output_dir

        # Initialize embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize vector store
        self.vectorstore = Chroma(
            collection_name=f"case_{case_id}",
            embedding_function=self.embeddings,
            persist_directory=f"{output_dir}/vector_db"
        )

    def index_timeline(self, timeline_csv: str):
        """Index timeline events for querying."""
        import pandas as pd

        df = pd.read_csv(timeline_csv)

        # Create documents
        documents = []
        for _, row in df.iterrows():
            doc_text = f"""
            Timestamp: {row['timestamp']}
            Event Type: {row['event_type']}
            Source: {row['source']}
            Description: {row['description']}
            User: {row.get('user', 'N/A')}
            Process: {row.get('process', 'N/A')}
            """

            documents.append({
                'text': doc_text,
                'metadata': {
                    'type': 'timeline',
                    'timestamp': row['timestamp'],
                    'source': row['source']
                }
            })

        # Index documents
        self.vectorstore.add_texts(
            texts=[doc['text'] for doc in documents],
            metadatas=[doc['metadata'] for doc in documents]
        )

    def index_artifacts(self, artifacts_dir: str):
        """Index all forensic artifacts."""
        # Index different artifact types
        self.index_processes(f"{artifacts_dir}/processes.csv")
        self.index_network(f"{artifacts_dir}/network.csv")
        self.index_registry(f"{artifacts_dir}/registry.csv")
        self.index_files(f"{artifacts_dir}/files.csv")

    def index_iocs(self, iocs_csv: str):
        """Index IOCs for querying."""
        import pandas as pd

        df = pd.read_csv(iocs_csv)

        documents = []
        for _, row in df.iterrows():
            doc_text = f"""
            IOC Type: {row['type']}
            Value: {row['value']}
            Context: {row['context']}
            Severity: {row['severity']}
            First Seen: {row['first_seen']}
            """

            documents.append({
                'text': doc_text,
                'metadata': {
                    'type': 'ioc',
                    'ioc_type': row['type'],
                    'severity': row['severity']
                }
            })

        self.vectorstore.add_texts(
            texts=[doc['text'] for doc in documents],
            metadatas=[doc['metadata'] for doc in documents]
        )
```

#### AI Query Engine

**Module**: `ai/query_engine.py`

```python
from langchain.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class ForensicQueryEngine:
    """
    AI-powered query engine for forensic data.

    Capabilities:
    - Natural language querying
    - Timeline analysis
    - IOC correlation
    - Investigation suggestions
    """

    def __init__(self, case_id: str, vector_store: Chroma):
        self.case_id = case_id
        self.vector_store = vector_store

        # Initialize local LLM
        self.llm = LlamaCpp(
            model_path="/opt/rivendell/models/llama-3-70b.gguf",
            n_ctx=4096,
            n_batch=512,
            temperature=0.1,  # Lower temperature for factual responses
            max_tokens=2048
        )

        # Create retrieval chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 10}),
            return_source_documents=True
        )

        # Forensic-specific prompt template
        self.prompt_template = PromptTemplate(
            template="""You are a digital forensics expert analyzing case {case_id}.

Context from investigation:
{context}

Analyst Question: {question}

Provide a detailed forensic analysis answer. Include:
1. Direct answer to the question
2. Supporting evidence from the context
3. Relevant timestamps or artifact sources
4. Any security concerns or red flags
5. Suggested follow-up investigation steps

Answer:""",
            input_variables=["case_id", "context", "question"]
        )

    def query(self, question: str) -> dict:
        """
        Query forensic data using natural language.

        Args:
            question: Natural language question

        Returns:
            dict with answer and source documents
        """
        result = self.qa_chain({"query": question})

        return {
            'answer': result['result'],
            'sources': [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in result['source_documents']
            ]
        }

    def suggest_investigation_paths(self) -> list:
        """Suggest investigation paths based on findings."""
        # Query for suspicious activities
        suspicious = self.query(
            "What suspicious activities or anomalies have been detected?"
        )

        # Generate suggestions
        suggestions_prompt = f"""
        Based on these suspicious activities:
        {suspicious['answer']}

        Suggest 5 specific investigation paths to pursue.
        """

        suggestions = self.llm(suggestions_prompt)

        return suggestions.split('\n')

    def generate_summary(self) -> str:
        """Generate case summary."""
        summary_prompt = f"""
        Generate a comprehensive summary of case {self.case_id} including:
        1. Key findings
        2. Timeline of significant events
        3. Identified IOCs
        4. MITRE ATT&CK techniques detected
        5. Recommendations
        """

        return self.llm(summary_prompt)
```

#### Web Interface

**Module**: `ai/web_interface.py`

```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()

# Store active query engines
query_engines = {}

@app.get("/ai/chat/{case_id}")
async def ai_chat_interface(case_id: str):
    """Render AI chat interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rivendell AI Assistant - Case {case_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            #chat-container {{ max-width: 800px; margin: 0 auto; }}
            #messages {{ height: 500px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; }}
            #input-container {{ margin-top: 10px; }}
            #question-input {{ width: 80%; padding: 10px; }}
            #send-btn {{ padding: 10px 20px; }}
            .message {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
            .user-message {{ background: #e3f2fd; text-align: right; }}
            .ai-message {{ background: #f1f8e9; }}
            .source {{ font-size: 0.8em; color: #666; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div id="chat-container">
            <h1>Rivendell AI Assistant</h1>
            <p>Case ID: {case_id}</p>
            <div id="messages"></div>
            <div id="input-container">
                <input type="text" id="question-input" placeholder="Ask a question about the investigation...">
                <button id="send-btn" onclick="sendQuestion()">Send</button>
            </div>
        </div>

        <script>
            const ws = new WebSocket('ws://localhost:8000/ai/ws/{case_id}');

            ws.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                displayAIMessage(data.answer, data.sources);
            }};

            function sendQuestion() {{
                const input = document.getElementById('question-input');
                const question = input.value;

                if (question.trim()) {{
                    displayUserMessage(question);
                    ws.send(JSON.stringify({{question: question}}));
                    input.value = '';
                }}
            }}

            function displayUserMessage(message) {{
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML += `<div class="message user-message">${{message}}</div>`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }}

            function displayAIMessage(answer, sources) {{
                const messagesDiv = document.getElementById('messages');
                let sourcesHtml = '';

                if (sources && sources.length > 0) {{
                    sourcesHtml = '<div class="source">Sources: ';
                    sources.forEach(src => {{
                        sourcesHtml += `${{src.metadata.source}} | `;
                    }});
                    sourcesHtml += '</div>';
                }}

                messagesDiv.innerHTML += `<div class="message ai-message">${{answer}}${{sourcesHtml}}</div>`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }}

            // Send on Enter key
            document.getElementById('question-input').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    sendQuestion();
                }}
            }});
        </script>
    </body>
    </html>
    """.format(case_id=case_id)

    return HTMLResponse(content=html)

@app.websocket("/ai/ws/{case_id}")
async def websocket_endpoint(websocket: WebSocket, case_id: str):
    """WebSocket endpoint for AI queries."""
    await websocket.accept()

    # Get or create query engine
    if case_id not in query_engines:
        # Load query engine for this case
        # query_engines[case_id] = ForensicQueryEngine.load(case_id)
        pass

    try:
        while True:
            # Receive question
            data = await websocket.receive_json()
            question = data['question']

            # Query AI
            result = query_engines[case_id].query(question)

            # Send response
            await websocket.send_json(result)

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

#### CLI Interface

**Module**: `cli/ai.py`

```python
#!/usr/bin/env python3
"""
Rivendell AI Assistant CLI

Usage:
    rivendell ai index CASE-001 /output/CASE-001
    rivendell ai query CASE-001 "What PowerShell commands were executed?"
    rivendell ai summary CASE-001
    rivendell ai suggest CASE-001
"""

import argparse
from ai.indexer import ForensicDataIndexer
from ai.query_engine import ForensicQueryEngine

def index_case(case_id: str, output_dir: str):
    """Index case data for AI querying."""
    print(f"[*] Indexing case {case_id}...")

    indexer = ForensicDataIndexer(case_id, output_dir)

    # Index all artifacts
    indexer.index_timeline(f"{output_dir}/timeline/timeline.csv")
    indexer.index_artifacts(f"{output_dir}/processed")
    indexer.index_iocs(f"{output_dir}/analysis/iocs.csv")

    print(f"[+] Indexing complete!")

def query_case(case_id: str, question: str):
    """Query case using AI."""
    # Load query engine
    engine = ForensicQueryEngine.load(case_id)

    # Query
    print(f"\n[?] {question}\n")
    result = engine.query(question)

    # Display answer
    print(f"[AI] {result['answer']}\n")

    # Display sources
    if result['sources']:
        print("[Sources]")
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['metadata']['source']} - {source['metadata']['type']}")

def main():
    parser = argparse.ArgumentParser(description="Rivendell AI Assistant")
    subparsers = parser.add_subparsers(dest='command')

    # Index command
    index_parser = subparsers.add_parser('index', help='Index case data')
    index_parser.add_argument('case_id', help='Case ID')
    index_parser.add_argument('output_dir', help='Case output directory')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query case data')
    query_parser.add_argument('case_id', help='Case ID')
    query_parser.add_argument('question', help='Question to ask')

    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Generate case summary')
    summary_parser.add_argument('case_id', help='Case ID')

    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Suggest investigation paths')
    suggest_parser.add_argument('case_id', help='Case ID')

    args = parser.parse_args()

    if args.command == 'index':
        index_case(args.case_id, args.output_dir)
    elif args.command == 'query':
        query_case(args.case_id, args.question)
    elif args.command == 'summary':
        engine = ForensicQueryEngine.load(args.case_id)
        print(engine.generate_summary())
    elif args.command == 'suggest':
        engine = ForensicQueryEngine.load(args.case_id)
        suggestions = engine.suggest_investigation_paths()
        print("\n[Suggested Investigation Paths]")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")

if __name__ == '__main__':
    main()
```

### 5.4 Example Queries

**Timeline Questions:**
```
"What PowerShell commands were executed?"
"Show me all network connections to external IPs"
"What files were created in the last hour before the incident?"
"Which processes were running at 2025-11-12 14:30:00?"
```

**Correlation Questions:**
```
"What events are related to IP address 192.168.1.100?"
"Show me all activity by user 'administrator'"
"What happened before the malicious file was executed?"
"Are there any IOCs related to PowerShell activity?"
```

**Investigation Questions:**
```
"What MITRE ATT&CK techniques were detected?"
"What persistence mechanisms were found?"
"Show me evidence of lateral movement"
"What data exfiltration indicators are present?"
```

**Summary Questions:**
```
"Summarize the attack timeline"
"What are the key findings?"
"What should I investigate next?"
"Generate an executive summary"
```

### 5.5 Configuration

**File**: `config/ai.yml`

```yaml
ai_agent:
  enabled: true

  model:
    type: local  # local, api (OpenAI, Anthropic)
    path: "/opt/rivendell/models/llama-3-70b.gguf"
    context_length: 4096
    temperature: 0.1
    max_tokens: 2048

  embedding:
    model: "sentence-transformers/all-MiniLM-L6-v2"
    device: "cuda"  # cuda, cpu

  vector_db:
    type: "chroma"  # chroma, qdrant
    persist_dir: "/opt/rivendell/data/vector_db"
    collection_prefix: "case_"

  indexing:
    auto_index: true
    index_on_analysis_complete: true
    artifacts_to_index:
      - timeline
      - iocs
      - processes
      - network
      - registry
      - files

  web_interface:
    enabled: true
    port: 8001
    websocket_enabled: true

  privacy:
    local_only: true
    no_external_apis: true
    data_retention_days: 365
```

### Implementation Steps

**Week 1-2**: Data Indexing
- Implement ForensicDataIndexer
- Index timeline, IOCs, artifacts
- Vector database setup

**Week 3-4**: Query Engine
- Deploy local LLM (Llama 3)
- Implement ForensicQueryEngine
- Create forensic-specific prompts

**Week 5**: Web Interface
- Create React-based chat UI
- WebSocket real-time communication
- Source citation display

**Week 6**: CLI Interface
- Implement CLI commands
- Integration with analysis pipeline
- Auto-indexing on analysis complete

**Week 7**: Testing & Optimization
- Query accuracy testing
- Response time optimization
- Model fine-tuning

---

## Implementation Timeline

### Phase 1: MITRE ATT&CK (Weeks 1-4)
- ✅ Week 1: Auto-updater
- ✅ Week 2: Technique mapper
- ✅ Week 3: Dashboard generator
- ✅ Week 4: Testing & integration

### Phase 2: Standalone Coverage (Weeks 5-8)
- ✅ Week 5: Real-time analyzer
- ✅ Week 6: Elrond integration
- ✅ Week 7: Standalone dashboard
- ✅ Week 8: SIEM integration

### Phase 3: Enhanced Artifacts (Weeks 9-14)
- ✅ Week 9-10: WMI parsing
- ✅ Week 11-12: macOS artifacts
- ✅ Week 13-14: Linux artifacts

### Phase 4: Cloud Forensics (Weeks 15-21)
- ✅ Week 15-16: AWS support
- ✅ Week 17-18: Azure support
- ✅ Week 19-20: GCP support
- ✅ Week 21: Integration & docs

### Phase 5: AI Agent (Weeks 22-28)
- ✅ Week 22-23: Data indexing
- ✅ Week 24-25: Query engine
- ✅ Week 26: Web interface
- ✅ Week 27: CLI interface
- ✅ Week 28: Testing & optimization

**Total Duration**: 28 weeks (~7 months)

---

## Dependencies

### Python Packages
```txt
# MITRE ATT&CK
stix2>=3.0.0
taxii2-client>=2.3.0

# Cloud providers
boto3>=1.28.0              # AWS
azure-mgmt-compute>=30.0.0 # Azure
azure-identity>=1.14.0
google-cloud-compute>=1.14.0  # GCP
google-cloud-logging>=3.5.0

# AI/ML
langchain>=0.1.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
llama-cpp-python>=0.2.0

# Artifact parsing
python-evtx>=0.7.4
pytsk3>=20230125
```

### External Tools
```bash
# macOS unified log parser
pip install UnifiedLogReader

# WMI repository parser
pip install python-cim

# Cloud CLIs (optional)
aws-cli
azure-cli
gcloud
```

### System Requirements
```
CPU: 8+ cores (for AI model)
RAM: 32GB+ (16GB for LLM inference)
Disk: 200GB+ (for AI models and vector DB)
GPU: Optional but recommended for AI (NVIDIA with CUDA)
```

---

## Testing Strategy

### Unit Tests
- MITRE updater and mapper
- Cloud acquisition modules
- Artifact parsers
- AI query engine

### Integration Tests
- End-to-end cloud acquisition
- Real-time MITRE coverage
- AI indexing pipeline

### Performance Tests
- Large dataset querying
- Concurrent AI queries
- Vector DB scaling

### Security Tests
- Cloud credential handling
- AI data privacy
- SIEM connection security

---

## Documentation

Each feature will include:
- ✅ User guide
- ✅ API documentation
- ✅ Configuration examples
- ✅ Troubleshooting guide
- ✅ Best practices

---

**Status**: Implementation Guide Complete
**Next Step**: Begin Phase 1 - MITRE ATT&CK Integration

---

This implementation guide will be updated as features are developed and refined based on testing and user feedback.

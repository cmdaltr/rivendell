"""
Default configuration values for Rivendell DFIR Suite

Centralizes hardcoded values found throughout the codebase.
"""

import os
from pathlib import Path


# ===== Directory Paths =====

# Default temporary directory
DEFAULT_TEMP_DIR = os.getenv('RIVENDELL_TEMP_DIR', '/tmp/rivendell')

# Default acquisition output directory
DEFAULT_ACQUISITION_DIR = os.getenv('RIVENDELL_ACQUISITION_DIR', '/tmp/gandalf/acquisitions')

# Default analysis output directory
DEFAULT_ANALYSIS_DIR = os.getenv('RIVENDELL_ANALYSIS_DIR', '/output')

# Default evidence directory
DEFAULT_EVIDENCE_DIR = os.getenv('RIVENDELL_EVIDENCE_DIR', '/evidence')


# ===== File Operations =====

# Default chunk size for file operations (256KB)
DEFAULT_CHUNK_SIZE = 262144

# Maximum file tree depth for collection
DEFAULT_MAX_DEPTH = 3


# ===== Encryption =====

# Default salt for password-based encryption
DEFAULT_ENCRYPTION_SALT = b"isengard.pork"

# PBKDF2 iterations (OWASP 2023 recommendation)
DEFAULT_PBKDF2_ITERATIONS = 480000

# Default encryption key filename
DEFAULT_KEY_FILENAME = "shadowfax.key"


# ===== Memory Configuration =====

# Memory thresholds for heap size calculation (bytes)
MEMORY_THRESHOLDS = {
    '256m': 2_000_000_000,      # < 2GB
    '512m': 4_000_000_000,      # 2-4GB
    '1g': 8_000_000_000,        # 4-8GB
    '2g': 16_000_000_000,       # 8-16GB
    '4g': 32_000_000_000,       # 16-32GB
}


# ===== SIEM Configuration =====

# Splunk defaults
SPLUNK_DEFAULT_PORT = 8088
SPLUNK_API_PORT = 8089
SPLUNK_DEFAULT_INDEX = "rivendell"
SPLUNK_DEFAULT_SOURCETYPE = "rivendell:forensics"
SPLUNK_HEC_ENDPOINT = "/services/collector/event"
SPLUNK_API_ENDPOINT = "/services/search/jobs"

# Elasticsearch defaults
ELASTIC_DEFAULT_PORT = 9200
ELASTIC_DEFAULT_SCHEME = "https"
ELASTIC_DEFAULT_INDEX = "rivendell-forensics"
ELASTIC_BULK_ENDPOINT = "/_bulk"
ELASTIC_INDEX_TEMPLATE_ENDPOINT = "/_index_template"

# Kibana defaults
KIBANA_DEFAULT_PORT = 5601


# ===== Tool Paths =====

# Common tool installation paths (searched in order)
TOOL_SEARCH_PATHS = [
    '/usr/bin',
    '/usr/local/bin',
    '/opt/local/bin',
    '/usr/sbin',
    '/usr/local/sbin',
    '/opt',
]

# Specific tool paths (override if needed)
TOOL_PATHS = {
    'volatility': '/usr/local/bin/vol.py',
    'plaso': '/usr/local/bin/log2timeline.py',
    'yara': '/usr/bin/yara',
    'clamscan': '/usr/bin/clamscan',
    'exiftool': '/usr/bin/exiftool',
    'tsk_recover': '/usr/bin/tsk_recover',
    'mmls': '/usr/bin/mmls',
    'fls': '/usr/bin/fls',
    'icat': '/usr/bin/icat',
}

# Splunk installation paths
SPLUNK_INSTALL_PATHS = [
    '/opt/splunk',
    '/Applications/Splunk',
    'C:\\Program Files\\Splunk',
]

# Elasticsearch installation paths
ELASTIC_INSTALL_PATHS = [
    '/usr/share/elasticsearch',
    '/opt/elasticsearch',
    '/etc/elasticsearch',
]


# ===== System Configuration Files =====

# Elasticsearch configuration files
ELASTIC_CONFIG_FILES = {
    'service': '/usr/lib/systemd/system/elasticsearch.service',
    'jvm': '/etc/elasticsearch/jvm.options',
    'config': '/etc/elasticsearch/elasticsearch.yml',
}

# Kibana configuration files
KIBANA_CONFIG_FILES = {
    'config': '/etc/kibana/kibana.yml',
}

# Splunk configuration files
SPLUNK_CONFIG_FILES = {
    'inputs': 'etc/apps/rivendell/local/inputs.conf',
    'props': 'etc/apps/rivendell/local/props.conf',
    'tags': 'etc/apps/rivendell/local/tags.conf',
    'indexes': 'etc/system/local/indexes.conf',
}


# ===== Artifact Collection =====

# Standard artifact subdirectories
ARTIFACT_SUBDIRS = [
    'memory',
    'logs',
    'registry',
    'prefetch',
    'browsers',
    'users',
    'system',
    'network',
    'tmp',
]

# Browser artifact types
BROWSER_TYPES = ['chrome', 'firefox', 'edge', 'safari']

# Browser artifact files
BROWSER_ARTIFACTS = {
    'chrome': ['History', 'Bookmarks', 'Preferences', 'Web Data', 'Cookies'],
    'firefox': ['places.sqlite', 'favicons.sqlite', 'cookies.sqlite', 'prefs.js'],
    'edge': ['History', 'Bookmarks', 'Preferences', 'Web Data'],
    'safari': ['History.db', 'Bookmarks.plist', 'Cookies.binarycookies'],
}


# ===== Log Configuration =====

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Default log level
DEFAULT_LOG_LEVEL = 'INFO'

# Audit log filename
DEFAULT_AUDIT_LOG = 'log.audit'

# Metadata log filename
DEFAULT_META_LOG = 'log.meta'


# ===== Network Configuration =====

# SSH default port
SSH_DEFAULT_PORT = 22

# PowerShell remoting ports
PSREMOTING_HTTP_PORT = 5985
PSREMOTING_HTTPS_PORT = 5986

# Connection timeouts (seconds)
DEFAULT_SSH_TIMEOUT = 30
DEFAULT_HTTP_TIMEOUT = 30


# ===== Archive Configuration =====

# Default archive format
DEFAULT_ARCHIVE_FORMAT = 'tar.gz'

# Supported archive formats
SUPPORTED_ARCHIVE_FORMATS = ['zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz']

# Default compression level (0-9)
DEFAULT_COMPRESSION_LEVEL = 6


# ===== Analysis Configuration =====

# Timeline analysis tools
TIMELINE_TOOL = 'plaso'

# Memory analysis tool
MEMORY_TOOL = 'volatility3'

# Default Volatility plugins
DEFAULT_VOLATILITY_PLUGINS = [
    'windows.pslist',
    'windows.psscan',
    'windows.netscan',
    'windows.malfind',
    'windows.dlllist',
]


# ===== Output Configuration =====

# Output formats
OUTPUT_FORMATS = ['csv', 'json', 'xlsx']

# Default output format
DEFAULT_OUTPUT_FORMAT = 'csv'


# ===== Resource Limits =====

# Maximum concurrent processes
DEFAULT_MAX_WORKERS = 4

# Process timeout (seconds)
DEFAULT_PROCESS_TIMEOUT = 300

# Maximum file size for processing (bytes, 10GB)
DEFAULT_MAX_FILE_SIZE = 10_737_418_240


# ===== Web Interface =====

# Default web server host
DEFAULT_WEB_HOST = '0.0.0.0'

# Default web server port
DEFAULT_WEB_PORT = 8000

# API prefix
API_PREFIX = '/api'

# WebSocket endpoint
WS_ENDPOINT = '/ws'


def get_temp_dir() -> str:
    """Get temporary directory path."""
    return DEFAULT_TEMP_DIR


def get_acquisition_dir() -> str:
    """Get acquisition output directory."""
    return DEFAULT_ACQUISITION_DIR


def get_analysis_dir() -> str:
    """Get analysis output directory."""
    return DEFAULT_ANALYSIS_DIR


def get_evidence_dir() -> str:
    """Get evidence directory."""
    return DEFAULT_EVIDENCE_DIR


def get_chunk_size() -> int:
    """Get default chunk size for file operations."""
    return DEFAULT_CHUNK_SIZE

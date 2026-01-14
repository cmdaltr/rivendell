"""
Artemis wrapper for forensic artifact parsing.

Artemis is a comprehensive Rust-based forensic parser that supports offline analysis
of Windows artifacts via --alt-file and --alt-dir parameters.

Supported artifacts:
- prefetch, eventlogs, mft, shimcache, amcache, registry, userassist,
- shellbags, usnjrnl, bits, srum, search, tasks, services, shortcuts,
- jumplists, recyclebin, outlook, wmipersist

See: https://github.com/puffyCid/artemis
"""

import json
import os
import subprocess
from datetime import datetime
from typing import Optional, Dict, List

from rivendell.audit import write_audit_log_entry

ARTEMIS_PATH = "/usr/local/bin/artemis"

# MITRE ATT&CK technique mappings for artefact types
ARTEFACT_MITRE_MAPPING = {
    "prefetch": {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactics": ["Execution"],
        "groups": ["APT28", "APT29", "Lazarus Group", "FIN7", "Wizard Spider"]
    },
    "eventlogs": {
        "technique_id": "T1070.001",
        "technique_name": "Clear Windows Event Logs",
        "tactics": ["Defense Evasion"],
        "groups": ["APT28", "APT29", "APT41", "Lazarus Group"]
    },
    "mft": {
        "technique_id": "T1070.006",
        "technique_name": "Timestomp",
        "tactics": ["Defense Evasion"],
        "groups": ["APT28", "APT29", "APT41", "Lazarus Group"]
    },
    "shimcache": {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactics": ["Execution"],
        "groups": ["APT28", "APT29", "Turla", "Lazarus Group"]
    },
    "amcache": {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactics": ["Execution"],
        "groups": ["APT28", "APT29", "Turla", "FIN7"]
    },
    "registry": {
        "technique_id": "T1112",
        "technique_name": "Modify Registry",
        "tactics": ["Defense Evasion"],
        "groups": ["APT28", "APT29", "Turla", "Lazarus Group"]
    },
    "userassist": {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactics": ["Execution"],
        "groups": ["APT28", "APT29", "Turla"]
    },
    "shellbags": {
        "technique_id": "T1083",
        "technique_name": "File and Directory Discovery",
        "tactics": ["Discovery"],
        "groups": ["APT28", "APT29", "Turla", "Lazarus Group", "OilRig"]
    },
    "usnjrnl": {
        "technique_id": "T1070.004",
        "technique_name": "File Deletion",
        "tactics": ["Defense Evasion"],
        "groups": ["APT28", "APT29", "Turla", "Lazarus Group"]
    },
    "bits": {
        "technique_id": "T1197",
        "technique_name": "BITS Jobs",
        "tactics": ["Defense Evasion", "Persistence"],
        "groups": ["APT41", "Leviathan", "Turla"]
    },
    "srum": {
        "technique_id": "T1049",
        "technique_name": "System Network Connections Discovery",
        "tactics": ["Discovery"],
        "groups": ["APT28", "APT29", "Turla", "Lazarus Group"]
    },
    "search": {
        "technique_id": "T1083",
        "technique_name": "File and Directory Discovery",
        "tactics": ["Discovery"],
        "groups": ["APT28", "APT29", "Turla"]
    },
    "tasks": {
        "technique_id": "T1053.005",
        "technique_name": "Scheduled Task",
        "tactics": ["Execution", "Persistence", "Privilege Escalation"],
        "groups": ["APT28", "APT29", "Lazarus Group", "FIN7", "Wizard Spider"]
    },
    "services": {
        "technique_id": "T1543.003",
        "technique_name": "Windows Service",
        "tactics": ["Persistence", "Privilege Escalation"],
        "groups": ["APT28", "Turla", "Lazarus Group", "FIN7"]
    },
    "shortcuts": {
        "technique_id": "T1547.009",
        "technique_name": "Shortcut Modification",
        "tactics": ["Persistence", "Privilege Escalation"],
        "groups": ["APT28", "APT29", "Turla"]
    },
    "jumplists": {
        "technique_id": "T1083",
        "technique_name": "File and Directory Discovery",
        "tactics": ["Discovery"],
        "groups": ["APT28", "APT29", "Turla"]
    },
    "recyclebin": {
        "technique_id": "T1070.004",
        "technique_name": "File Deletion",
        "tactics": ["Defense Evasion"],
        "groups": ["APT28", "APT29", "Lazarus Group"]
    },
    "outlook": {
        "technique_id": "T1114.001",
        "technique_name": "Local Email Collection",
        "tactics": ["Collection"],
        "groups": ["APT28", "APT29", "Turla", "OilRig", "Kimsuky"]
    },
    "wmipersist": {
        "technique_id": "T1546.003",
        "technique_name": "WMI Event Subscription",
        "tactics": ["Persistence", "Privilege Escalation"],
        "groups": ["APT29", "Turla", "Leviathan"]
    },
}


def enrich_with_mitre(json_path: str, artifact_type: str) -> bool:
    """
    Fast MITRE enrichment for all artifact files.

    Instead of loading the entire JSON and scanning every field, this:
    1. Streams through the file line by line
    2. Only extracts and scans relevant fields based on artifact type
    3. Uses simple string matching for artifact-specific patterns

    This is much faster than full regex scanning.
    """
    import re
    import traceback

    print(f"        [DEBUG-ENRICH] ENTERED enrich_with_mitre() for {os.path.basename(json_path)}, artifact_type={artifact_type}", flush=True)

    try:
        print(f"        [DEBUG-ENRICH] Inside try block, about to determine case_dir", flush=True)
        # Determine techniques file path at CASE level
        # json_path example: /output/case/image.E01/artefacts/cooked/browsers/file.json
        # We need: /output/case/mitre_techniques.txt (alongside rivendell_audit.log)
        current_dir = os.path.dirname(json_path)
        case_dir = None

        # Walk up looking for known directory markers
        check_dir = current_dir
        for _ in range(8):  # Max 8 levels up
            dir_name = os.path.basename(check_dir)
            parent = os.path.dirname(check_dir)

            if dir_name == "cooked":
                # Found cooked, go up THREE levels: cooked -> artefacts -> image -> case
                case_dir = os.path.dirname(os.path.dirname(os.path.dirname(check_dir)))
                break
            elif dir_name == "artefacts":
                # Found artefacts, go up TWO levels: artefacts -> image -> case
                case_dir = os.path.dirname(os.path.dirname(check_dir))
                break
            elif os.path.exists(os.path.join(check_dir, "rivendell_audit.log")):
                # Found case level (has audit log)
                case_dir = check_dir
                break

            check_dir = parent

        # Fallback: if we didn't find a marker, use original directory
        if not case_dir:
            case_dir = current_dir

        techniques_file_path = os.path.join(case_dir, "mitre_techniques.txt")
        print(f"        [DEBUG-ENRICH] Determined techniques_file_path: {techniques_file_path}", flush=True)
        os.makedirs(case_dir, exist_ok=True)

        # Base technique for artifact type
        print(f"        [DEBUG-ENRICH] Looking up base technique for artifact_type.lower()='{artifact_type.lower()}'", flush=True)
        base_technique = ARTEFACT_MITRE_MAPPING.get(artifact_type.lower(), {}).get("technique_id")
        print(f"        [DEBUG-ENRICH] Base technique: {base_technique}", flush=True)

        found_techniques = set()
        if base_technique:
            found_techniques.add(base_technique)

        # Get artifact-appropriate patterns and field extractors
        print(f"        [DEBUG-ENRICH] Calling _get_patterns_for_artifact('{artifact_type}')", flush=True)
        patterns, field_pattern = _get_patterns_for_artifact(artifact_type)
        print(f"        [DEBUG-ENRICH] Got patterns (count={len(patterns) if patterns else 0}), field_pattern={field_pattern if field_pattern else 'None'}", flush=True)

        if not patterns:
            print(f"        [DEBUG-ENRICH] No patterns for this artifact type, writing base technique and returning", flush=True)
            # No specific patterns for this artifact type, just write base technique
            if base_technique:
                with open(techniques_file_path, 'a') as f:
                    f.write(f"{base_technique}\n")
            return True

        print(f"        [DEBUG-ENRICH] Compiling field_regex", flush=True)
        field_regex = re.compile(field_pattern, re.IGNORECASE)

        lines_processed = 0
        print(f"        [DEBUG-ENRICH] About to open and read json_path: {json_path}", flush=True)
        try:
            with open(json_path, 'r', errors='ignore') as f:
                for line in f:
                    lines_processed += 1
                    # Progress every 500k lines
                    if lines_processed % 500000 == 0:
                        print(f"    ...scanned {lines_processed:,} lines, found {len(found_techniques)} techniques", flush=True)

                    # Extract relevant fields from this line
                    matches = field_regex.findall(line)
                    for match in matches:
                        match_lower = match.lower()
                        for tech_id, indicators in patterns.items():
                            for indicator in indicators:
                                if indicator in match_lower:
                                    found_techniques.add(tech_id)
                                    break

            print(f"        [DEBUG-ENRICH] Finished reading {lines_processed} lines, found {len(found_techniques)} techniques", flush=True)

            # Write all found techniques
            print(f"        [DEBUG-ENRICH] About to write {len(found_techniques)} techniques to {techniques_file_path}", flush=True)
            with open(techniques_file_path, 'a') as f:
                for tech_id in found_techniques:
                    f.write(f"{tech_id}\n")

            print(f"        [DEBUG-ENRICH] Successfully wrote techniques, returning True", flush=True)
            return True

        except Exception as e:
            print(f"        [DEBUG-ENRICH] Inner Exception during fast scan: {e}", flush=True)
            print(f"    WARNING: Error during fast scan: {e}", flush=True)
            if base_technique:
                with open(techniques_file_path, 'a') as f:
                    f.write(f"{base_technique}\n")
            print(f"        [DEBUG-ENRICH] Returning False from inner exception", flush=True)
            return False

    except NameError as e:
        print(f"        [DEBUG-ENRICH] *** OUTER NameError CAUGHT in enrich_with_mitre() ***", flush=True)
        print(f"    *** CRITICAL ERROR: NameError in enrich_with_mitre(): {e}", flush=True)
        print(f"    *** Full traceback:", flush=True)
        traceback.print_exc()
        print(f"        [DEBUG-ENRICH] Returning False from NameError", flush=True)
        return False
    except Exception as e:
        print(f"        [DEBUG-ENRICH] *** OUTER Exception CAUGHT in enrich_with_mitre() ***", flush=True)
        print(f"    *** CRITICAL ERROR: Unexpected error in enrich_with_mitre(): {e}", flush=True)
        print(f"    *** Full traceback:", flush=True)
        traceback.print_exc()
        print(f"        [DEBUG-ENRICH] Returning False from outer exception", flush=True)
        return False


def _get_patterns_for_artifact(artifact_type: str):
    """
    Return appropriate MITRE patterns and field extractor based on artifact type.

    Returns:
        tuple: (patterns_dict, field_regex_pattern) or (None, None) if no patterns apply
    """
    artifact_lower = artifact_type.lower()

    # ========================================
    # CROSS-PLATFORM: Event Logs (Windows evtx, macOS/Linux logs)
    # ========================================
    if artifact_lower in ["eventlogs", "evtx", "evt", "logs", "log"]:
        patterns = {
            # Windows Event ID based techniques
            "T1070.001": ["1102", "104"],  # Log clearing
            "T1053.005": ["4698", "4699", "4700", "4701", "4702"],  # Scheduled tasks
            "T1136": ["4720", "4722", "4738"],  # Account creation/modification
            "T1098": ["4728", "4732", "4756"],  # Group membership changes
            "T1003": ["4656", "4663"],  # Credential access (LSASS)
            "T1021.001": ["4624", "4625"],  # RDP logon
            "T1021.002": ["5140", "5145"],  # SMB access
            "T1547.001": ["7045"],  # Service installation
            "T1059.001": ["4104", "4103", "powershell", ".ps1", "-enc", "-encodedcommand"],  # PowerShell
            "T1569.002": ["7045", "4697"],  # Service execution
            # Cross-platform command/process patterns
            "T1059.003": ["cmd.exe", "cmd /c"],  # Windows cmd
            "T1059.004": ["/bin/sh", "/bin/bash", "/bin/zsh", "sh -c"],  # Unix shell
            "T1059.005": ["wscript", "cscript", ".vbs"],  # VBScript
            "T1059.006": ["python", "/usr/bin/python"],  # Python
            "T1218": ["mshta", "regsvr32", "rundll32", "msiexec", "certutil"],
            "T1003.001": ["mimikatz", "procdump", "lsass"],
            "T1105": ["psexec", "paexec", "bitsadmin", "certutil", "curl", "wget"],
            # macOS/Linux specific
            "T1053.003": ["cron", "crontab"],  # Cron
            "T1543.002": ["systemctl", "service"],  # Systemd
            "T1548.003": ["sudo", "doas"],  # Sudo abuse
        }
        # Extract Event IDs and message content
        field_pattern = r'"(?:event_id|EventID|eventid|message|Message|CommandLine|command_line|msg|log)"\s*:\s*"?([^",}\]]+)"?'
        return patterns, field_pattern

    # ========================================
    # WINDOWS-ONLY: Registry (may contain paths, files, and command lines)
    # ========================================
    if artifact_lower in ["registry", "reg", "shimcache", "amcache", "userassist"]:
        patterns = {
            # Registry-specific
            "T1547.001": ["\\run", "\\runonce", "\\explorer\\shell", "\\winlogon"],  # Autostart
            "T1546.001": ["\\classes\\", "\\shell\\open\\command"],  # File associations
            "T1112": ["\\policies\\", "\\software\\microsoft\\"],  # Registry modification
            "T1562.001": ["\\windows defender\\", "disableantispyware"],  # Disable security
            # Command lines in registry values
            "T1059.001": ["powershell", ".ps1", "-enc", "-encodedcommand", "-nop", "-w hidden"],
            "T1059.003": ["cmd.exe", "cmd /c", "cmd /k"],
            "T1059.005": ["wscript", "cscript", ".vbs"],
            "T1218": ["mshta", "regsvr32", "rundll32", "msiexec", "certutil"],
            # Files referenced in registry
            "T1003": ["mimikatz", "procdump", "lsass", "sam", "system", "security", "pwdump"],
            "T1105": ["psexec", "paexec", "bitsadmin"],
            "T1219": ["anydesk", "teamviewer", "vnc", "logmein"],
        }
        field_pattern = r'"(?:path|key|value|name|full_path|data|command|arguments)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # WINDOWS-ONLY: Prefetch
    # ========================================
    if artifact_lower in ["prefetch", "pf"]:
        patterns = {
            "T1059": ["powershell", "cmd.exe", "wscript", "cscript", "python", "perl"],
            "T1218": ["mshta", "regsvr32", "rundll32", "msiexec", "certutil", "cmstp"],
            "T1003": ["mimikatz", "procdump", "pwdump", "gsecdump", "secretsdump"],
            "T1105": ["psexec", "paexec", "bitsadmin", "curl", "wget"],
            "T1036": ["svchost", "csrss", "lsass", "services"],  # Masquerading
            "T1070.004": ["sdelete", "cipher"],  # File deletion
            "T1219": ["anydesk", "teamviewer", "vnc", "logmein", "screenconnect"],
        }
        field_pattern = r'"(?:filename|name|path|executable)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # WINDOWS-ONLY: MFT, USNJrnl
    # ========================================
    if artifact_lower in ["mft", "usnjrnl"]:
        patterns = {
            "T1059": [".ps1", ".vbs", ".js", ".bat", ".cmd", "powershell", "wscript", "cscript"],
            "T1036": ["svchost", "csrss", "lsass", "services", "winlogon", "explorer"],
            "T1003": ["mimikatz", "procdump", "lsass.dmp", "sam.save", "system.save", "ntds.dit", "pwdump"],
            "T1105": ["psexec", "paexec", "certutil", "bitsadmin"],
            "T1218": ["mshta", "regsvr32", "rundll32", "msiexec"],
            "T1547": ["\\run\\", "\\runonce\\", "startup"],
            "T1070": ["wevtutil", "fsutil", "$recycle", "sdelete"],
            "T1219": ["anydesk", "teamviewer", "vnc", "logmein", "ammyy"],
            "T1486": [".encrypted", ".locked", ".crypto", "readme.txt", "decrypt"],  # Ransomware
        }
        field_pattern = r'"(?:full_path|filename|name|path)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # CROSS-PLATFORM: Generic file listings
    # ========================================
    if artifact_lower in ["filelisting", "files"]:
        patterns = {
            # Cross-platform scripting
            "T1059.001": [".ps1", "powershell"],  # PowerShell (Windows)
            "T1059.004": [".sh", "/bin/bash", "/bin/sh", "/bin/zsh"],  # Unix shell
            "T1059.005": [".vbs", "wscript", "cscript"],  # VBScript (Windows)
            "T1059.006": [".py", "python"],  # Python
            "T1059.007": [".js"],  # JavaScript
            # Cross-platform tools
            "T1003": ["mimikatz", "procdump", "pwdump", "hashdump"],
            "T1105": ["psexec", "paexec", "curl", "wget", "nc", "netcat"],
            "T1219": ["anydesk", "teamviewer", "vnc", "logmein"],
            "T1486": [".encrypted", ".locked", ".crypto", "ransom"],  # Ransomware
            # Persistence locations
            "T1547": ["startup", "autostart", ".bashrc", ".zshrc", "crontab", "launchagents"],
        }
        field_pattern = r'"(?:full_path|filename|name|path)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # MACOS/LINUX: Journal files
    # ========================================
    if artifact_lower in ["journal", "journalctl", "syslog"]:
        patterns = {
            "T1059.004": ["/bin/sh", "/bin/bash", "/bin/zsh", "sh -c"],  # Unix shell
            "T1059.006": ["python", "/usr/bin/python"],  # Python
            "T1053.003": ["cron", "crontab"],  # Cron
            "T1543.002": ["systemctl", "service"],  # Systemd
            "T1070.002": ["rm ", "unlink", "shred"],  # Log deletion
            "T1105": ["curl", "wget", "nc", "netcat", "scp", "rsync"],
        }
        field_pattern = r'"(?:message|msg|command|unit|exe)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # MACOS-ONLY: Plists (may contain command lines)
    # ========================================
    if artifact_lower in ["plist", "launchagent", "launchdaemon", "loginitems"]:
        patterns = {
            # Plist-specific persistence
            "T1543.001": ["launchagents"],  # Launch Agent
            "T1543.004": ["launchdaemons"],  # Launch Daemon
            "T1547.015": ["loginitems", "loginwindow"],  # Login Items
            # Command lines in plists
            "T1059.002": ["osascript", "applescript"],  # AppleScript
            "T1059.004": ["/bin/sh", "/bin/bash", "/bin/zsh", "sh -c"],  # Unix shell
            "T1059.006": ["python", "/usr/bin/python", "python3"],  # Python
            "T1059.007": ["node", "javascript"],  # JavaScript
            # Suspicious binaries
            "T1105": ["curl", "wget", "nc", "netcat"],
            "T1553.001": ["quarantine", "xattr"],  # Gatekeeper bypass
        }
        field_pattern = r'"(?:path|program|label|command|arguments|ProgramArguments|Program)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # BROWSER ARTIFACTS (Cross-platform)
    # ========================================
    if artifact_lower in ["browser", "chromium", "firefox", "safari", "history", "downloads"]:
        patterns = {
            "T1567": ["drive.google", "dropbox", "onedrive", "mega.nz", "wetransfer"],  # Exfil to cloud
            "T1102": ["pastebin", "hastebin", "ghostbin"],  # Web service C2
            "T1189": ["exploit", "payload", ".exe", ".dll", ".scr"],  # Drive-by
            "T1566.002": ["login", "account", "verify", "suspended"],  # Phishing keywords
        }
        field_pattern = r'"(?:url|path|title|filename)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # WINDOWS-ONLY: Shellbags (may contain command lines in target paths)
    # ========================================
    if artifact_lower in ["shellbags"]:
        patterns = {
            "T1083": ["users\\", "documents", "desktop", "downloads"],  # File discovery
            "T1005": ["confidential", "password", "secret", "backup"],  # Data from local system
            "T1025": ["usb", "removable"],  # Removable media
            # Command-related paths
            "T1059": ["powershell", "cmd.exe", ".ps1", ".bat", ".vbs"],
            "T1218": ["mshta", "regsvr32", "rundll32"],
        }
        field_pattern = r'"(?:path|name|full_path|target)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # CROSS-PLATFORM: Scheduled Tasks / Cron
    # ========================================
    if artifact_lower in ["tasks", "schtasks", "scheduled", "cron", "crontab"]:
        patterns = {
            # Task-specific
            "T1053.005": ["schtasks", "at.exe"],  # Windows scheduled tasks
            "T1053.003": ["cron", "crontab", "* * *"],  # Cron (macOS/Linux)
            # Command lines in tasks
            "T1059.001": ["powershell", ".ps1", "-enc", "-encodedcommand"],
            "T1059.003": ["cmd.exe", "cmd /c"],
            "T1059.004": ["/bin/sh", "/bin/bash", "sh -c"],
            "T1059.005": ["wscript", "cscript", ".vbs"],
            "T1059.006": ["python", "/usr/bin/python"],
            "T1218": ["mshta", "regsvr32", "rundll32", "certutil"],
            "T1105": ["curl", "wget", "psexec", "bitsadmin"],
        }
        field_pattern = r'"(?:path|command|action|name|arguments|program|schedule)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # WINDOWS-ONLY: Services (contain command lines)
    # ========================================
    if artifact_lower in ["services"]:
        patterns = {
            # Service-specific
            "T1543.003": ["\\system32\\", "\\syswow64\\"],  # Windows Service paths
            "T1569.002": ["psexec", "paexec"],  # Service Execution
            "T1036": ["svchost", "csrss", "lsass"],  # Masquerading
            # Command lines in service configs
            "T1059.001": ["powershell", ".ps1", "-enc"],
            "T1059.003": ["cmd.exe", "cmd /c"],
            "T1218": ["mshta", "regsvr32", "rundll32", "msiexec"],
            "T1105": ["certutil", "bitsadmin"],
            "T1219": ["anydesk", "teamviewer", "vnc"],
        }
        field_pattern = r'"(?:path|binary_path|name|display_name|command|arguments|ImagePath)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # CROSS-PLATFORM: Generic text log files (.log)
    # Could contain commands, paths, errors, etc.
    # ========================================
    if artifact_lower in ["logfile", "textlog", "syslog", "auth", "secure", "messages"]:
        patterns = {
            # Cross-platform commands
            "T1059.001": ["powershell", ".ps1", "-enc", "-encodedcommand"],
            "T1059.003": ["cmd.exe", "cmd /c"],
            "T1059.004": ["/bin/sh", "/bin/bash", "/bin/zsh", "sh -c"],
            "T1059.006": ["python", "/usr/bin/python"],
            # Authentication/credential access
            "T1110": ["failed password", "authentication failure", "invalid user"],
            "T1078": ["accepted password", "session opened", "successful login"],
            "T1548.003": ["sudo", "doas", "root"],
            # Persistence
            "T1053.003": ["cron", "crontab"],
            "T1543.002": ["systemctl", "service"],
            # Lateral movement / tools
            "T1021.004": ["ssh", "sshd", "accepted publickey"],
            "T1105": ["curl", "wget", "scp", "rsync", "nc", "netcat"],
            # Suspicious activity
            "T1070.002": ["log deleted", "cleared", "truncated"],
            "T1003": ["mimikatz", "procdump", "lsass", "hashdump"],
        }
        field_pattern = r'"(?:message|msg|log|line|content|text|data)"\s*:\s*"([^"]+)"'
        return patterns, field_pattern

    # ========================================
    # DEFAULT: Generic patterns (fallback)
    # ========================================
    patterns = {
        "T1059": [".ps1", ".vbs", ".bat", ".sh", "powershell", "cmd.exe", "/bin/bash"],
        "T1003": ["mimikatz", "procdump", "lsass"],
        "T1105": ["psexec", "certutil", "curl", "wget"],
    }
    field_pattern = r'"(?:path|name|command|value|message|data)"\s*:\s*"([^"]+)"'
    return patterns, field_pattern


def enrich_json_with_mitre(json_path: str, artifact_type: str, techniques_file_path: str = None) -> bool:
    """
    Enrich a JSON file with MITRE ATT&CK metadata.

    Uses the comprehensive MitreEnrichment class for content-based pattern matching.
    Also writes technique IDs to the techniques file for Navigator layer generation.

    Args:
        json_path: Path to JSON file
        artifact_type: Type of artifact (prefetch, eventlogs, etc.)
        techniques_file_path: Optional path to techniques file for Navigator

    Returns:
        True if successful
    """
    try:
        # Use the comprehensive MitreEnrichment class for content-based pattern matching
        from rivendell.post.mitre.enrichment import MitreEnrichment
        enrichment = MitreEnrichment()

        # Determine techniques file path if not provided
        if not techniques_file_path:
            # Go up from cooked dir to CASE level, write mitre_techniques.txt there
            # json_path example: /output/case/image.E01/artefacts/cooked/browsers/file.json
            # We need: /output/case/mitre_techniques.txt (alongside rivendell_audit.log)
            current_dir = os.path.dirname(json_path)
            case_dir = None

            # Walk up looking for known directory markers
            check_dir = current_dir
            for _ in range(8):  # Max 8 levels up
                dir_name = os.path.basename(check_dir)
                parent = os.path.dirname(check_dir)

                if dir_name == "cooked":
                    # Found cooked, go up THREE levels: cooked -> artefacts -> image -> case
                    case_dir = os.path.dirname(os.path.dirname(os.path.dirname(check_dir)))
                    break
                elif dir_name == "artefacts":
                    # Found artefacts, go up TWO levels: artefacts -> image -> case
                    case_dir = os.path.dirname(os.path.dirname(check_dir))
                    break
                elif os.path.exists(os.path.join(check_dir, "rivendell_audit.log")):
                    # Found case level (has audit log)
                    case_dir = check_dir
                    break

                check_dir = parent

            # Fallback: if we didn't find a marker, use original directory
            if not case_dir:
                case_dir = current_dir

            techniques_file_path = os.path.join(case_dir, "mitre_techniques.txt")

        # Ensure directory exists
        os.makedirs(os.path.dirname(techniques_file_path), exist_ok=True)

        # Open techniques file in append mode and enrich the JSON
        with open(techniques_file_path, 'a') as techniques_file:
            return enrichment.enrich_json_file_streaming(json_path, techniques_file, artifact_type)

    except ImportError:
        # Fallback to simple mapping if enrichment module not available
        mitre_data = ARTEFACT_MITRE_MAPPING.get(artifact_type.lower())
        if not mitre_data:
            return False

        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            # Handle both single records and arrays
            if isinstance(data, list):
                for record in data:
                    if isinstance(record, dict):
                        record["mitre_technique_id"] = mitre_data["technique_id"]
                        record["mitre_technique_name"] = mitre_data["technique_name"]
                        record["mitre_tactics"] = mitre_data["tactics"]
                        record["mitre_groups"] = mitre_data["groups"]
            elif isinstance(data, dict):
                data["mitre_technique_id"] = mitre_data["technique_id"]
                data["mitre_technique_name"] = mitre_data["technique_name"]
                data["mitre_tactics"] = mitre_data["tactics"]
                data["mitre_groups"] = mitre_data["groups"]

            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Write technique ID to file if path provided
            if techniques_file_path and mitre_data:
                with open(techniques_file_path, 'a') as f:
                    f.write(f"{mitre_data['technique_id']}\n")

            return True

        except Exception:
            return False
    except Exception:
        return False


def artemis_available() -> bool:
    """Check if Artemis binary is available."""
    return os.path.exists(ARTEMIS_PATH)


def run_artemis(
    artifact: str,
    output_dir: str,
    alt_file: Optional[str] = None,
    alt_dir: Optional[str] = None,
    output_filename: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Run Artemis to parse a forensic artifact using CLI acquire mode.

    Args:
        artifact: Artifact type (prefetch, eventlogs, mft, shimcache, etc.)
        output_dir: Directory to write output files
        alt_file: Alternative file path for single-file artifacts
        alt_dir: Alternative directory path for multi-file artifacts
        output_filename: Desired output filename (without .json extension).
                        If provided, output will be renamed to this name.

    Returns:
        Tuple of (success: bool, error_message: str)
    """
    if not artemis_available():
        return False, f"Artemis not found at {ARTEMIS_PATH}"

    # Build command using CLI acquire mode
    # NOTE: --format and --output-dir must come BEFORE the artifact subcommand
    cmd = [
        ARTEMIS_PATH,
        "acquire",
        "--format", "JSON",
        "--output-dir", output_dir,
        artifact,
    ]

    # Artifact-specific argument names (artemis has different param names per artifact)
    # Mapping: artifact -> (file_arg, dir_arg)
    artifact_args = {
        "prefetch": (None, "--alt-dir"),           # only supports --alt-dir
        "eventlogs": ("--alt-file", "--alt-dir"),  # supports both
        "mft": ("--alt-file", None),               # only --alt-file
        "shimcache": ("--alt-file", None),         # only --alt-file
        "usnjrnl": ("--alt-path", None),           # uses --alt-path not --alt-file
        "amcache": ("--alt-file", None),           # only --alt-file
        "registry": ("--alt-file", None),          # only --alt-file
        "jumplists": ("--alt-file", None),         # only --alt-file
        "wmipersist": (None, "--alt-dir"),         # only --alt-dir
        "userassist": ("--alt-file", None),        # only --alt-file
        "shellbags": ("--alt-file", None),         # only --alt-file
        "bits": ("--alt-file", None),              # only --alt-file
        "srum": ("--alt-file", None),              # only --alt-file
        "search": ("--alt-file", None),            # only --alt-file
        "tasks": ("--alt-file", None),             # only --alt-file
        "services": ("--alt-file", None),          # only --alt-file
        "shortcuts": ("--alt-file", None),         # only --alt-file
        "recyclebin": ("--alt-file", None),        # only --alt-file
        "outlook": ("--alt-file", None),           # only --alt-file
    }

    file_arg, dir_arg = artifact_args.get(artifact, ("--alt-file", "--alt-dir"))

    # Add alt_file or alt_dir if specified (these go after the artifact subcommand)
    if alt_file and file_arg:
        cmd.extend([file_arg, alt_file])
    elif alt_dir and dir_arg:
        cmd.extend([dir_arg, alt_dir])

    try:
        import sys
        import threading
        import time as time_module

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Progress indicator for long-running operations
        stop_progress = threading.Event()
        def show_progress():
            start_time = time_module.time()
            # Use proper display name for artifacts
            display_name = "$MFT" if artifact == "mft" else artifact
            while not stop_progress.is_set():
                elapsed = int(time_module.time() - start_time)
                if elapsed > 0 and elapsed % 30 == 0:  # Every 30 seconds
                    print(f" -> still processing {display_name}... ({elapsed}s elapsed)", flush=True)
                stop_progress.wait(1)

        progress_thread = threading.Thread(target=show_progress, daemon=True)
        progress_thread.start()

        stdout_data, stderr_data = process.communicate()
        stop_progress.set()
        progress_thread.join(timeout=1)

        if process.returncode != 0:
            stderr_text = stderr_data.decode('utf-8', errors='replace') if stderr_data else ''
            stdout_text = stdout_data.decode('utf-8', errors='replace') if stdout_data else ''
            return False, f"{stderr_text} {stdout_text}"[:500]

        # Artemis outputs to a 'local_collector' subdirectory - move files up
        import shutil
        import glob
        local_collector_dir = os.path.join(output_dir, "local_collector")
        if os.path.exists(local_collector_dir):
            json_files = glob.glob(os.path.join(local_collector_dir, "*.json"))

            # For MFT, merge all JSON files into a single file
            if artifact == "mft" and len(json_files) > 1:
                merged_data = []
                for jf in json_files:
                    try:
                        with open(jf, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                merged_data.extend(data)
                            else:
                                merged_data.append(data)
                    except:
                        pass
                # Write merged file - always use journal_mft.json for MFT
                merged_path = os.path.join(output_dir, "journal_mft.json")
                with open(merged_path, 'w') as f:
                    json.dump(merged_data, f)
                # Clean up individual files
                for jf in json_files:
                    os.remove(jf)
            elif len(json_files) == 1:
                # Single output file - rename appropriately
                if artifact == "mft":
                    # Always use journal_mft.json for MFT
                    dest = os.path.join(output_dir, "journal_mft.json")
                elif output_filename:
                    # Use provided output filename
                    dest = os.path.join(output_dir, f"{output_filename}.json")
                else:
                    # Keep original name
                    dest = os.path.join(output_dir, os.path.basename(json_files[0]))
                shutil.move(json_files[0], dest)
            elif len(json_files) > 1 and output_filename:
                # Multiple files but we have a desired output name - merge them
                merged_data = []
                for jf in json_files:
                    try:
                        with open(jf, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                merged_data.extend(data)
                            else:
                                merged_data.append(data)
                    except:
                        pass
                # Write merged file with desired name
                merged_path = os.path.join(output_dir, f"{output_filename}.json")
                with open(merged_path, 'w') as f:
                    json.dump(merged_data, f)
                # Clean up individual files
                for jf in json_files:
                    os.remove(jf)
            else:
                # Multiple files and no specific output name - move with original names
                for f in glob.glob(os.path.join(local_collector_dir, "*.json")):
                    dest = os.path.join(output_dir, os.path.basename(f))
                    shutil.move(f, dest)

            # Remove local_collector directory
            try:
                shutil.rmtree(local_collector_dir)
            except:
                pass

        return True, ""

    except Exception as e:
        return False, str(e)


def extract_with_artemis(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    artifact_type: str,
    artifact_file: Optional[str] = None,
    artifact_dir: Optional[str] = None,
    output_subdir: str = "",
    fixed_output_name: Optional[str] = None,
) -> bool:
    """
    Extract artifacts using Artemis with proper logging.

    Args:
        verbosity: Verbosity level
        vssimage: VSS image identifier
        output_directory: Base output directory
        img: Image identifier
        vss_path_insert: VSS path component
        stage: Processing stage name
        artifact_type: Artemis artifact type
        artifact_file: Path to artifact file (for --alt-file)
        artifact_dir: Path to artifact directory (for --alt-dir)
        output_subdir: Subdirectory name for output (e.g., "prefetch", "evt")
        fixed_output_name: Override output filename (without .json extension)

    Returns:
        True if successful, False otherwise
    """
    if not artemis_available():
        entry, prnt = "{},{},{},'{}' (skipped - artemis not found)\n".format(
            datetime.now().isoformat(),
            vssimage.replace("'", ""),
            stage,
            artifact_type,
        ), " -> {} -> skipped '{}' for {} (artemis not found)".format(
            datetime.now().isoformat().replace("T", " "),
            artifact_type,
            vssimage,
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        return False

    # Determine output path
    cooked_base = (
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
    )

    if output_subdir:
        cooked_dir = cooked_base + output_subdir + "/"
    else:
        cooked_dir = cooked_base

    # Create output directory if needed
    os.makedirs(cooked_dir, exist_ok=True)

    # Log start - only show filename, not full path
    artifact_display = os.path.basename(artifact_file) if artifact_file else (os.path.basename(artifact_dir.rstrip('/')) if artifact_dir else "system")
    entry, prnt = "{},{},{},'{}'\n".format(
        datetime.now().isoformat(),
        vssimage.replace("'", ""),
        stage,
        artifact_type,
    ), " -> {} {} '{}' for {}".format(
        stage,
        artifact_type,
        artifact_display,
        vssimage,
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)

    # Derive output filename from the original artefact (without extension)
    if fixed_output_name:
        # Use the fixed output name if provided
        output_name = fixed_output_name
    elif artifact_file:
        # Get filename without path, then remove extension
        base_name = os.path.basename(artifact_file)
        # Remove extension (handle .evtx, .pf, etc.)
        output_name = os.path.splitext(base_name)[0]
    elif artifact_dir:
        # For directories, use the directory name
        output_name = os.path.basename(artifact_dir.rstrip('/'))
    else:
        output_name = None

    # Run Artemis
    success, error = run_artemis(
        artifact=artifact_type,
        output_dir=cooked_dir,
        alt_file=artifact_file,
        alt_dir=artifact_dir,
        output_filename=output_name,
    )

    if not success:
        error_msg = error.replace('\n', ' ').replace(',', ';').replace("'", "")[:200]
        # Always print errors regardless of verbosity
        print(
            " -> {} -> WARNING: artemis {} failed for {}: {}".format(
                datetime.now().isoformat().replace('T', ' '),
                artifact_type,
                vssimage,
                error_msg[:100]
            )
        )
        return False

    # Fast MITRE enrichment - scan JSON files for artifact-specific patterns
    import glob
    import traceback
    print(f"    [DEBUG] About to enrich MITRE for artifact_type='{artifact_type}'", flush=True)
    print(f"    [DEBUG] Local variables: {list(locals().keys())}", flush=True)
    try:
        for json_file in glob.glob(os.path.join(cooked_dir, "*.json")):
            print(f"    [DEBUG] Enriching file: {os.path.basename(json_file)}", flush=True)
            print(f"    [DEBUG] About to call enrich_with_mitre with json_file={json_file}, artifact_type={artifact_type}", flush=True)
            try:
                result = enrich_with_mitre(json_file, artifact_type)
                print(f"    [DEBUG] enrich_with_mitre returned: {result}", flush=True)
            except Exception as inner_e:
                print(f"    [DEBUG] *** Exception during enrich_with_mitre call: {type(inner_e).__name__}: {inner_e}", flush=True)
                print(f"    [DEBUG] *** Full traceback:", flush=True)
                traceback.print_exc()
                print(f"    [DEBUG] *** Locals at error: {locals()}", flush=True)
                raise
        print(f"    [DEBUG] MITRE enrichment completed successfully", flush=True)
    except NameError as e:
        print(f"    [DEBUG] *** NameError caught in extract_with_artemis(): {e}", flush=True)
        print(f"    [DEBUG] *** Full traceback:", flush=True)
        traceback.print_exc()
        print(f"    [DEBUG] *** artifact_type={artifact_type}, cooked_dir={cooked_dir}", flush=True)
    except Exception as e:
        print(f"    [DEBUG] *** Exception caught in extract_with_artemis(): {e}", flush=True)
        traceback.print_exc()

    print(f"    [DEBUG] extract_with_artemis() about to return True", flush=True)
    return True


# Convenience functions for specific artifact types

def extract_prefetch(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    prefetch_dir: str,
) -> bool:
    """Extract Windows Prefetch files using Artemis, logging each file individually."""
    if not os.path.exists(prefetch_dir):
        return False

    # Get list of .pf files
    pf_files = [f for f in os.listdir(prefetch_dir) if f.lower().endswith('.pf')]

    if not pf_files:
        return False

    success_count = 0
    for pf_file in pf_files:
        pf_path = os.path.join(prefetch_dir, pf_file)
        # Log each prefetch file being processed
        print(
            "     processing prefetch file '{}'".format(pf_file)
        )
        result = extract_with_artemis(
            verbosity=verbosity,
            vssimage=vssimage,
            output_directory=output_directory,
            img=img,
            vss_path_insert=vss_path_insert,
            stage=stage,
            artifact_type="prefetch",
            artifact_file=pf_path,
            output_subdir="prefetch",
        )
        if result:
            success_count += 1

    return success_count > 0


def extract_eventlogs(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    evtx_file: Optional[str] = None,
    evtx_dir: Optional[str] = None,
) -> bool:
    """Extract Windows Event Logs using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="eventlogs",
        artifact_file=evtx_file,
        artifact_dir=evtx_dir,
        output_subdir="evt",
    )


def extract_mft(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    mft_file: str,
) -> bool:
    """Extract MFT using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="mft",
        artifact_file=mft_file,
        output_subdir="",
    )


def extract_shimcache(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    system_hive: str,
) -> bool:
    """Extract Shimcache from SYSTEM registry hive using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="shimcache",
        artifact_file=system_hive,
        output_subdir="",  # Output directly to cooked/ as shimcache.json
        fixed_output_name="shimcache",  # Force output name to shimcache.json
    )


def extract_amcache(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    amcache_file: str,
) -> bool:
    """Extract Amcache using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="amcache",
        artifact_file=amcache_file,
        output_subdir="amcache",
    )


def extract_userassist(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    ntuser_file: str,
) -> bool:
    """Extract UserAssist from NTUSER.DAT using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="userassist",
        artifact_file=ntuser_file,
        output_subdir="userassist",
    )


def extract_shellbags(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    registry_file: str,
) -> bool:
    """Extract Shellbags from NTUSER.DAT or UsrClass.dat using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="shellbags",
        artifact_file=registry_file,
        output_subdir="shellbags",
    )


def extract_usnjrnl(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    usnjrnl_file: str,
) -> bool:
    """Extract USN Journal using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="usnjrnl",
        artifact_file=usnjrnl_file,
        output_subdir="",  # Output directly to cooked/ as journal_usn.json
        fixed_output_name="journal_usn",  # Force output name to journal_usn.json
    )


def extract_srum(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    srum_file: str,
) -> bool:
    """Extract SRUM database using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="srum",
        artifact_file=srum_file,
        output_subdir="srum",
    )


def extract_bits(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    bits_file: str,
) -> bool:
    """Extract BITS database using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="bits",
        artifact_file=bits_file,
        output_subdir="bits",
    )


def extract_tasks(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    task_file: str,
) -> bool:
    """Extract Scheduled Task using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="tasks",
        artifact_file=task_file,
        output_subdir="tasks",
    )


def extract_services(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    system_hive: str,
) -> bool:
    """Extract Windows Services from SYSTEM hive using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="services",
        artifact_file=system_hive,
        output_subdir="services",
    )


def extract_shortcuts(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    lnk_file: str,
) -> bool:
    """Extract Windows shortcut (LNK) file using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="shortcuts",
        artifact_file=lnk_file,
        output_subdir="shortcuts",
    )


def extract_jumplists(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    jumplist_file: str,
) -> bool:
    """Extract Jumplist file using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="jumplists",
        artifact_file=jumplist_file,
        output_subdir="jumplists",
    )


def extract_recyclebin(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    recycle_file: str,
) -> bool:
    """Extract Recycle Bin entry using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="recyclebin",
        artifact_file=recycle_file,
        output_subdir="recyclebin",
    )


def extract_outlook(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    ost_file: str,
) -> bool:
    """Extract Outlook OST file using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="outlook",
        artifact_file=ost_file,
        output_subdir="outlook",
    )


def extract_wmipersist(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    wmi_dir: str,
) -> bool:
    """Extract WMI persistence from repository directory using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="wmipersist",
        artifact_dir=wmi_dir,
        output_subdir="",  # Output directly to cooked/ as wbem.json
        fixed_output_name="wbem",  # Force output name to wbem.json
    )


def extract_search(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    search_file: str,
) -> bool:
    """Extract Windows Search database using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="search",
        artifact_file=search_file,
        output_subdir="search",
    )


def extract_registry(
    verbosity: str,
    vssimage: str,
    output_directory: str,
    img: str,
    vss_path_insert: str,
    stage: str,
    registry_file: str,
) -> bool:
    """Extract Windows Registry hive using Artemis."""
    return extract_with_artemis(
        verbosity=verbosity,
        vssimage=vssimage,
        output_directory=output_directory,
        img=img,
        vss_path_insert=vss_path_insert,
        stage=stage,
        artifact_type="registry",
        artifact_file=registry_file,
        output_subdir="registry",
    )

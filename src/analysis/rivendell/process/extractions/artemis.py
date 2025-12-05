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


def enrich_json_with_mitre(json_path: str, artifact_type: str) -> bool:
    """
    Enrich a JSON file with MITRE ATT&CK metadata.

    Args:
        json_path: Path to JSON file
        artifact_type: Type of artifact (prefetch, eventlogs, etc.)

    Returns:
        True if successful
    """
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

        return True

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
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_data, stderr_data = process.communicate()

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

    # Log start
    entry, prnt = "{},{},{},'{}'\n".format(
        datetime.now().isoformat(),
        vssimage.replace("'", ""),
        stage,
        artifact_type,
    ), " -> {} {} '{}' for {}".format(
        stage,
        artifact_type,
        artifact_file or artifact_dir or "system",
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

    # Enrich JSON files with MITRE ATT&CK metadata
    import glob
    for json_file in glob.glob(os.path.join(cooked_dir, "*.json")):
        enrich_json_with_mitre(json_file, artifact_type)

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

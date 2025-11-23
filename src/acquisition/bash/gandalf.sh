#!/usr/bin/env bash

#############################################################################
# Gandalf Bash - Remote Forensic Artifact Acquisition Tool
#
# A pure bash implementation for Linux/Unix forensic evidence collection
# Part of the Rivendell DF Acceleration Suite
#
# Usage: sudo ./gandalf.sh [ENCRYPTION] [MODE] [OPTIONS]
#
# Encryption: Key, Password, None
# Mode: Local, Remote
# Options: -o OUTPUT_DIR, -m (memory), -a (access times), -c (collect files)
#
#############################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Version
VERSION="2.0.0"

# Default values
ENCRYPTION_METHOD=""
ACQUISITION_MODE=""
OUTPUT_DIR="/tmp/gandalf/acquisitions"
MEMORY_DUMP=false
ACCESS_TIMES=false
COLLECT_FILES=false
HOSTS_FILE=""
REMOTE_USER=""
REMOTE_HOST=""
WORK_DIR="/tmp/gandalf"

# Banner function
print_banner() {
    cat << "EOF"
    ____                  __      __  ____
   / ___| __ _ _ __   __| | __ _ \ \/ /\ \
  | |  _ / _` | '_ \ / _` |/ _` | \  /  | |
  | |_| | (_| | | | | (_| | (_| | /  \  | |
   \____|\__,_|_| |_|\__,_|\__,_|/_/\_\ | |
                                         /_/
   Bash Edition - Remote Forensic Acquisition
   Version ${VERSION}

EOF
    local quotes=(
        "You shall pass... your artifacts to the analyst!"
        "A forensic analyst is never late, nor is he early..."
        "Even the smallest clue can change the course of the investigation"
        "Keep it secret, keep it safe... then decrypt it for analysis"
        "All we have to decide is what to do with the evidence given to us"
    )
    local random_quote=${quotes[$RANDOM % ${#quotes[@]}]}
    echo -e "${BLUE}   ${random_quote}${NC}\n"
}

# Usage function
usage() {
    echo "Usage: sudo $0 <Encryption> <Mode> [OPTIONS]"
    echo ""
    echo "Encryption Methods:"
    echo "  Key       - Generate and use encryption key file"
    echo "  Password  - Use password-based encryption"
    echo "  None      - No encryption"
    echo ""
    echo "Acquisition Modes:"
    echo "  Local     - Acquire from local system"
    echo "  Remote    - Acquire from remote hosts via SSH"
    echo ""
    echo "Options:"
    echo "  -o DIR    Output directory (default: /tmp/gandalf/acquisitions)"
    echo "  -m        Acquire memory dump"
    echo "  -a        Collect file access times"
    echo "  -c        Collect specific files from files.list"
    echo "  -h HOST   Remote hostname (for Remote mode)"
    echo "  -u USER   Remote username (for Remote mode)"
    echo "  -f FILE   Hosts file (for Remote mode batch)"
    echo ""
    echo "Examples:"
    echo "  sudo $0 None Local"
    echo "  sudo $0 Password Local -m -o /evidence"
    echo "  sudo $0 Key Remote -h 192.168.1.100 -u analyst"
    echo ""
    exit 1
}

# Check root privileges
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()

    for cmd in tar gzip ssh scp hostname date sha256sum; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done

    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Missing required dependencies: ${missing_deps[*]}"
        echo "Please install them before running this script"
        exit 1
    fi
}

# Parse arguments
parse_args() {
    if [ $# -lt 2 ]; then
        usage
    fi

    ENCRYPTION_METHOD="$1"
    ACQUISITION_MODE="$2"
    shift 2

    # Validate encryption method
    case "${ENCRYPTION_METHOD,,}" in
        key|password|none)
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Invalid encryption method: $ENCRYPTION_METHOD"
            usage
            ;;
    esac

    # Validate acquisition mode
    case "${ACQUISITION_MODE,,}" in
        local|remote)
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Invalid acquisition mode: $ACQUISITION_MODE"
            usage
            ;;
    esac

    # Parse options
    while getopts "o:mach:u:f:" opt; do
        case $opt in
            o) OUTPUT_DIR="$OPTARG" ;;
            m) MEMORY_DUMP=true ;;
            a) ACCESS_TIMES=true ;;
            c) COLLECT_FILES=true ;;
            h) REMOTE_HOST="$OPTARG" ;;
            u) REMOTE_USER="$OPTARG" ;;
            f) HOSTS_FILE="$OPTARG" ;;
            *) usage ;;
        esac
    done
}

# Initialize directories
init_directories() {
    local hostname="$1"
    local acq_dir="${OUTPUT_DIR}/${hostname}"

    mkdir -p "${acq_dir}/artefacts"/{memory,logs,conf,cron,services,browsers,user,tmp}

    echo "$acq_dir"
}

# Initialize audit log
init_audit_log() {
    local log_file="$1"
    echo "datetime,hostname,artefact,collected" > "$log_file"
}

# Initialize metadata log
init_meta_log() {
    local log_file="$1"
    echo "hostname,file_path,sha256_hash" > "$log_file"
}

# Log to audit
log_audit() {
    local log_file="$1"
    local hostname="$2"
    local artefact="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%6NZ")

    echo "${timestamp},${hostname},${artefact},collected" >> "$log_file"
}

# Collect file with hash
collect_file() {
    local source="$1"
    local dest="$2"
    local hostname="$3"
    local meta_log="$4"

    if [ -e "$source" ]; then
        # Create destination directory
        mkdir -p "$(dirname "$dest")"

        # Copy file preserving timestamps
        cp -p "$source" "$dest" 2>/dev/null || return 1

        # Calculate hash
        local hash=$(sha256sum "$dest" | awk '{print $1}')

        # Log to metadata
        echo "${hostname},${source},${hash}" >> "$meta_log"

        return 0
    fi
    return 1
}

# Collect volatile data
collect_volatile() {
    local acq_dir="$1"
    local hostname="$2"
    local audit_log="$3"

    echo -e "${BLUE}[*]${NC} Collecting volatile data..."

    # Platform information
    uname -a > "${acq_dir}/artefacts/host.info" 2>/dev/null || true
    log_audit "$audit_log" "$hostname" "host.info"

    # Process list
    ps aux > "${acq_dir}/artefacts/process.info" 2>/dev/null || true
    log_audit "$audit_log" "$hostname" "process.info"

    # Network connections
    if command -v ss &> /dev/null; then
        ss -tunap > "${acq_dir}/artefacts/ss.info" 2>/dev/null || true
        log_audit "$audit_log" "$hostname" "ss.info"
    fi

    if command -v netstat &> /dev/null; then
        netstat -tunap > "${acq_dir}/artefacts/netstat.info" 2>/dev/null || true
        log_audit "$audit_log" "$hostname" "netstat.info"
    fi

    # Loaded modules
    lsmod > "${acq_dir}/artefacts/lsmod.info" 2>/dev/null || true

    # Environment variables
    env > "${acq_dir}/artefacts/env.info" 2>/dev/null || true
}

# Collect memory dump
collect_memory() {
    local acq_dir="$1"
    local hostname="$2"
    local audit_log="$3"

    if [ "$MEMORY_DUMP" = false ]; then
        return 0
    fi

    echo -e "${BLUE}[*]${NC} Acquiring memory dump..."

    # Check for AVML
    if command -v avml &> /dev/null; then
        avml "${acq_dir}/artefacts/memory/${hostname}.mem" 2>/dev/null || {
            echo -e "${YELLOW}[!]${NC} Memory acquisition failed"
            return 1
        }
        log_audit "$audit_log" "$hostname" "memory/${hostname}.mem"
        echo -e "${GREEN}[+]${NC} Memory dump acquired"
    else
        echo -e "${YELLOW}[!]${NC} AVML not found, skipping memory acquisition"
    fi
}

# Collect filesystem artifacts
collect_artifacts() {
    local acq_dir="$1"
    local hostname="$2"
    local audit_log="$3"
    local meta_log="$4"

    echo -e "${BLUE}[*]${NC} Collecting filesystem artifacts..."

    # Define artifact mappings
    declare -A artifacts=(
        # Configuration files
        ["/etc/passwd"]="etc+passwd"
        ["/etc/shadow"]="etc+shadow"
        ["/etc/group"]="etc+group"
        ["/etc/hosts"]="etc+hosts"
        ["/etc/hostname"]="etc+hostname"
        ["/etc/fstab"]="etc+fstab"
        ["/etc/sudoers"]="conf/etc+sudoers"
        ["/etc/ssh/sshd_config"]="conf/etc+ssh+sshd_config"

        # Cron jobs
        ["/etc/crontab"]="cron/etc+crontab"

        # Logs (will collect directory)

        # System files
        ["/etc/timezone"]="etc+timezone"
        ["/etc/os-release"]="etc+os-release"
    )

    # Collect individual files
    for source in "${!artifacts[@]}"; do
        local dest_name="${artifacts[$source]}"
        if [ -n "$dest_name" ]; then
            # Has subdirectory
            if [[ "$dest_name" == *"/"* ]]; then
                local dest="${acq_dir}/artefacts/${dest_name}"
            else
                local dest="${acq_dir}/artefacts/${dest_name}"
            fi
        else
            # No subdirectory, just filename
            local dest="${acq_dir}/artefacts/$(basename $source)"
        fi

        if collect_file "$source" "$dest" "$hostname" "$meta_log"; then
            log_audit "$audit_log" "$hostname" "$source"
        fi
    done

    # Collect directories
    collect_directory "/var/log" "${acq_dir}/artefacts/logs" "$hostname" "$audit_log" "$meta_log"
    collect_directory "/etc/cron.d" "${acq_dir}/artefacts/cron" "$hostname" "$audit_log" "$meta_log"
    collect_directory "/etc/systemd" "${acq_dir}/artefacts/conf" "$hostname" "$audit_log" "$meta_log"

    # User directories (limited to key files)
    for user_home in /home/* /root; do
        if [ -d "$user_home" ]; then
            local username=$(basename "$user_home")
            collect_user_artifacts "$user_home" "$username" "$acq_dir" "$hostname" "$audit_log" "$meta_log"
        fi
    done
}

# Collect directory with depth limit
collect_directory() {
    local source_dir="$1"
    local dest_dir="$2"
    local hostname="$3"
    local audit_log="$4"
    local meta_log="$5"
    local max_depth="${6:-3}"

    if [ ! -d "$source_dir" ]; then
        return 1
    fi

    mkdir -p "$dest_dir"

    # Use find to collect files with depth limit
    while IFS= read -r -d '' file; do
        local rel_path="${file#$source_dir/}"
        local dest_file="${dest_dir}/$(echo "$rel_path" | tr '/' '+')"

        if collect_file "$file" "$dest_file" "$hostname" "$meta_log"; then
            log_audit "$audit_log" "$hostname" "$file"
        fi
    done < <(find "$source_dir" -maxdepth "$max_depth" -type f -print0 2>/dev/null)
}

# Collect user artifacts
collect_user_artifacts() {
    local user_home="$1"
    local username="$2"
    local acq_dir="$3"
    local hostname="$4"
    local audit_log="$5"
    local meta_log="$6"

    local user_dir="${acq_dir}/artefacts/user/${username}"
    mkdir -p "$user_dir"

    # Bash history
    collect_file "${user_home}/.bash_history" "${user_dir}/.bash_history" "$hostname" "$meta_log"
    collect_file "${user_home}/.bashrc" "${user_dir}/.bashrc" "$hostname" "$meta_log"
    collect_file "${user_home}/.profile" "${user_dir}/.profile" "$hostname" "$meta_log"

    # SSH keys and config
    if [ -d "${user_home}/.ssh" ]; then
        collect_directory "${user_home}/.ssh" "${user_dir}/ssh" "$hostname" "$audit_log" "$meta_log" 1
    fi

    # Browser artifacts
    collect_browser_artifacts "$user_home" "$username" "$acq_dir" "$hostname" "$audit_log" "$meta_log"
}

# Collect browser artifacts
collect_browser_artifacts() {
    local user_home="$1"
    local username="$2"
    local acq_dir="$3"
    local hostname="$4"
    local audit_log="$5"
    local meta_log="$6"

    local browser_dir="${acq_dir}/artefacts/browsers"

    # Chrome/Chromium
    local chrome_paths=(
        "${user_home}/.config/google-chrome/Default"
        "${user_home}/.config/chromium/Default"
    )

    for chrome_path in "${chrome_paths[@]}"; do
        if [ -d "$chrome_path" ]; then
            local chrome_dest="${browser_dir}/chrome/${username}"
            mkdir -p "$chrome_dest"

            for file in "History" "Bookmarks" "Preferences" "Web Data" "Cookies"; do
                if [ -f "${chrome_path}/${file}" ]; then
                    collect_file "${chrome_path}/${file}" "${chrome_dest}/${username}+${file}" "$hostname" "$meta_log"
                    log_audit "$audit_log" "$hostname" "${chrome_path}/${file}"
                fi
            done
        fi
    done

    # Firefox
    local firefox_path="${user_home}/.mozilla/firefox"
    if [ -d "$firefox_path" ]; then
        for profile in "${firefox_path}"/*.default*; do
            if [ -d "$profile" ]; then
                local firefox_dest="${browser_dir}/firefox/${username}"
                mkdir -p "$firefox_dest"

                for file in "places.sqlite" "favicons.sqlite" "cookies.sqlite" "prefs.js"; do
                    if [ -f "${profile}/${file}" ]; then
                        collect_file "${profile}/${file}" "${firefox_dest}/${username}+${file}" "$hostname" "$meta_log"
                        log_audit "$audit_log" "$hostname" "${profile}/${file}"
                    fi
                done
            fi
        done
    fi
}

# Create archive
create_archive() {
    local acq_dir="$1"
    local hostname="$2"
    local output_file="${OUTPUT_DIR}/${hostname}.tar.gz"

    echo -e "${BLUE}[*]${NC} Creating archive..."

    tar -czf "$output_file" -C "${acq_dir}" . 2>/dev/null || {
        echo -e "${RED}[ERROR]${NC} Failed to create archive"
        return 1
    }

    echo -e "${GREEN}[+]${NC} Archive created: $output_file"
    echo "$output_file"
}

# Encrypt archive
encrypt_archive() {
    local archive_file="$1"
    local hostname="$2"

    case "${ENCRYPTION_METHOD,,}" in
        none)
            return 0
            ;;
        key|password)
            echo -e "${YELLOW}[!]${NC} Encryption with openssl (AES-256-CBC)"

            if [ "${ENCRYPTION_METHOD,,}" = "key" ]; then
                # Generate random key
                local key_file="${OUTPUT_DIR}/shadowfax.key"
                openssl rand -base64 32 > "$key_file"
                echo -e "${GREEN}[+]${NC} Encryption key saved: $key_file"

                # Encrypt with key
                openssl enc -aes-256-cbc -salt -pbkdf2 -in "$archive_file" -out "${archive_file}.enc" -pass file:"$key_file"
            else
                # Password-based encryption
                echo -e "${BLUE}[*]${NC} Enter encryption password:"
                openssl enc -aes-256-cbc -salt -pbkdf2 -in "$archive_file" -out "${archive_file}.enc"
            fi

            if [ -f "${archive_file}.enc" ]; then
                rm -f "$archive_file"
                echo -e "${GREEN}[+]${NC} Archive encrypted: ${archive_file}.enc"
            else
                echo -e "${RED}[ERROR]${NC} Encryption failed"
                return 1
            fi
            ;;
    esac
}

# Local acquisition
acquire_local() {
    local hostname=$(hostname)
    local start_time=$(date +%s)

    echo -e "${GREEN}[+]${NC} Starting local acquisition for: $hostname"

    # Initialize
    local acq_dir=$(init_directories "$hostname")
    local audit_log="${acq_dir}/log.audit"
    local meta_log="${acq_dir}/log.meta"

    init_audit_log "$audit_log"
    init_meta_log "$meta_log"

    # Collect
    collect_volatile "$acq_dir" "$hostname" "$audit_log"
    collect_memory "$acq_dir" "$hostname" "$audit_log"
    collect_artifacts "$acq_dir" "$hostname" "$audit_log" "$meta_log"

    # Archive
    local archive_file=$(create_archive "$acq_dir" "$hostname")

    # Encrypt
    encrypt_archive "$archive_file" "$hostname"

    # Cleanup work directory
    rm -rf "$acq_dir"

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo -e "${GREEN}[+]${NC} Acquisition complete!"
    echo -e "${BLUE}[*]${NC} Duration: ${duration} seconds"
    echo -e "${BLUE}[*]${NC} Output: ${OUTPUT_DIR}/"
}

# Remote acquisition
acquire_remote() {
    if [ -z "$REMOTE_HOST" ] && [ -z "$HOSTS_FILE" ]; then
        echo -e "${RED}[ERROR]${NC} Remote mode requires -h HOST or -f HOSTS_FILE"
        exit 1
    fi

    if [ -z "$REMOTE_USER" ]; then
        echo -e "${BLUE}[*]${NC} Enter remote username:"
        read -r REMOTE_USER
    fi

    local hosts=()
    if [ -n "$HOSTS_FILE" ]; then
        while IFS= read -r line; do
            # Skip comments and empty lines
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ -z "$line" ]] && continue
            hosts+=("$line")
        done < "$HOSTS_FILE"
    else
        hosts=("$REMOTE_HOST")
    fi

    for host in "${hosts[@]}"; do
        echo -e "${GREEN}[+]${NC} Acquiring from remote host: $host"

        # Copy script to remote
        local remote_script="/tmp/gandalf_collect.sh"
        scp "$0" "${REMOTE_USER}@${host}:${remote_script}" || {
            echo -e "${RED}[ERROR]${NC} Failed to copy script to $host"
            continue
        }

        # Execute remotely
        ssh "${REMOTE_USER}@${host}" "sudo bash ${remote_script} ${ENCRYPTION_METHOD} Local -o /tmp/gandalf/acquisitions ${MEMORY_DUMP:+-m}" || {
            echo -e "${RED}[ERROR]${NC} Remote execution failed on $host"
            continue
        }

        # Retrieve archive
        local remote_file=$(ssh "${REMOTE_USER}@${host}" "ls -1 /tmp/gandalf/acquisitions/*.tar.gz* | head -1")
        if [ -n "$remote_file" ]; then
            scp "${REMOTE_USER}@${host}:${remote_file}" "${OUTPUT_DIR}/" || {
                echo -e "${RED}[ERROR]${NC} Failed to retrieve archive from $host"
                continue
            }

            # Cleanup remote
            ssh "${REMOTE_USER}@${host}" "sudo rm -rf /tmp/gandalf" || true

            echo -e "${GREEN}[+]${NC} Successfully acquired from $host"
        else
            echo -e "${RED}[ERROR]${NC} No archive found on $host"
        fi
    done
}

# Main function
main() {
    print_banner
    check_root
    check_dependencies
    parse_args "$@"

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    case "${ACQUISITION_MODE,,}" in
        local)
            acquire_local
            ;;
        remote)
            acquire_remote
            ;;
    esac
}

# Run main
main "$@"

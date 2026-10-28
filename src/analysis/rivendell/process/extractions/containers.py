"""Docker and Kubernetes node artefacts, as collected into raw/linux/ (process/linux_artefacts.py
routes them here).

- /var/lib/docker/containers/<id>/config.v2.json, with hostconfig.json beside it: one row per
  container, flagged when it can reach the host (privileged, the Docker socket, the host's
  namespaces, sensitive host paths, dangerous capabilities)
- /var/lib/docker/containers/<id>/<id>-json.log and /var/log/pods/.../<n>.log: container output
- gandalf+container_changes.csv: Gandalf's listing of each container's writable layer, which is
  everything that changed since the container's image
- /etc/kubernetes/manifests/*.yaml: static pods, which the kubelet runs with no API server involved

Every function returns rows; techniques are decided from the rows by the *_techniques functions,
only where a row justifies one.
"""

import csv
import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Host paths a container has no business mounting
SENSITIVE_MOUNTS = ("/", "/etc", "/root", "/proc", "/sys", "/dev", "/boot", "/var/lib/docker", "/var/lib/kubelet",
                    "/var/lib/containerd", "/home", "/usr", "/lib", "/var/log")
DOCKER_SOCKETS = ("/var/run/docker.sock", "/run/docker.sock", "/run/containerd/containerd.sock",
                  "/var/run/containerd/containerd.sock", "/var/run/crio/crio.sock", "/run/crio/crio.sock")
ESCAPE_CAPABILITIES = {"ALL", "SYS_ADMIN", "SYS_PTRACE", "SYS_MODULE", "DAC_READ_SEARCH", "SYS_RAWIO", "BPF"}
# Kubernetes' own static pods; anything else in the manifests directory was put there by someone
CONTROL_PLANE_PODS = re.compile(r"^(?:kube-apiserver|kube-controller-manager|kube-scheduler|etcd|kube-vip|haproxy|"
                                r"keepalived)(?:-|$)")
TEMP_PATHS = re.compile(r"^/(?:tmp|var/tmp|dev/shm|run)/|/\.[^/]+$")
# Files whose change inside a container is persistence or access, with the technique it implies
PERSISTENCE_FILES = (
    (re.compile(r"^/etc/(?:cron\.(?:d|daily|hourly|weekly|monthly)/|crontab$)|^/var/spool/cron/"), "cron", "T1053.003"),
    (re.compile(r"/\.ssh/authorized_keys2?$"), "SSH authorized keys", "T1098.004"),
    (re.compile(r"^/etc/ld\.so\.preload$"), "ld.so.preload", "T1574.006"),
    (re.compile(r"^/etc/(?:passwd|shadow)$"), "accounts", "T1136.001"),
    (re.compile(r"^/etc/(?:profile|bash\.bashrc|bashrc)$|^/etc/profile\.d/|/\.(?:bashrc|profile|bash_profile)$"),
     "shell startup", "T1546.004"),
)

HEADERS = {
    "docker_containers.csv": ["Container", "Name", "Image", "Command", "Created", "Started", "Finished", "Running",
                              "User", "Privileged", "PidMode", "NetworkMode", "IpcMode", "CapAdd", "SecurityOpt",
                              "Mounts", "Flag"],
    "container_logs.csv": ["Runtime", "Container", "Pod", "Namespace", "Stream", "LastWriteTime", "Message"],
    "container_changes.csv": ["Container", "Path", "Size", "Mode", "Kind", "SHA256", "LastWriteTime", "Flag"],
    "static_pods.csv": ["Source", "Name", "Namespace", "Images", "Command", "Flag"],
}


def _load_json(path: str) -> Dict:
    with open(path, encoding="utf-8", errors="replace") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def _sensitive(source: str) -> bool:
    source = source.rstrip("/") or "/"
    return source in SENSITIVE_MOUNTS or source.startswith(("/etc/", "/root/", "/proc/", "/sys/", "/dev/"))


def container_flags(privileged: bool, mounts: List[Dict[str, str]], pid_mode: str, network_mode: str,
                    ipc_mode: str, cap_add: List[str], security_opt: List[str]) -> List[str]:
    """Why a container could reach its host, or nothing for one that can't."""
    flags = []
    if privileged:
        flags.append("privileged")
    for mount in mounts:
        source = mount.get("Source", "")
        if source in DOCKER_SOCKETS:
            flags.append(f"container runtime socket mounted ({source})")
        elif _sensitive(source):
            flags.append(f"host path mounted {'read-write' if mount.get('RW') else 'read-only'} ({source})")
    if pid_mode == "host":
        flags.append("host PID namespace")
    if network_mode == "host":
        flags.append("host network")
    if ipc_mode == "host":
        flags.append("host IPC namespace")
    dangerous = sorted(c.upper().replace("CAP_", "") for c in cap_add
                       if c.upper().replace("CAP_", "") in ESCAPE_CAPABILITIES)
    if dangerous:
        flags.append("capabilities " + ", ".join(dangerous))
    if any(opt.replace("=", ":").lower() in ("seccomp:unconfined", "apparmor:unconfined") for opt in security_opt):
        flags.append("seccomp or AppArmor disabled")
    return flags


def docker_container_row(path: str, hostconfig: Optional[str] = None) -> Optional[Dict[str, str]]:
    """One container from its config.v2.json, and the hostconfig.json beside it when there is one."""
    config = _load_json(path)
    if not config.get("ID"):
        return None
    host = _load_json(hostconfig) if hostconfig and os.path.isfile(hostconfig) else {}
    state = config.get("State") or {}
    settings = config.get("Config") or {}
    mounts = [{"Source": m.get("Source", ""), "Destination": m.get("Destination", ""), "RW": bool(m.get("RW"))}
              for m in (config.get("MountPoints") or {}).values()]
    for bind in host.get("Binds") or []:  # source:destination[:options]
        parts = bind.split(":")
        if len(parts) >= 2 and not any(m["Source"] == parts[0] for m in mounts):
            mounts.append({"Source": parts[0], "Destination": parts[1],
                           "RW": not (len(parts) > 2 and "ro" in parts[2].split(","))})
    cap_add = host.get("CapAdd") or []
    security_opt = host.get("SecurityOpt") or []
    flags = container_flags(bool(host.get("Privileged")), mounts, host.get("PidMode") or "",
                            host.get("NetworkMode") or "", host.get("IpcMode") or "", cap_add, security_opt)
    command = " ".join([config.get("Path") or ""] + [str(a) for a in config.get("Args") or []]).strip()
    return {
        "Container": config["ID"][:12], "Name": (config.get("Name") or "").lstrip("/"),
        "Image": settings.get("Image") or config.get("Image", ""), "Command": command,
        "Created": config.get("Created", ""), "Started": state.get("StartedAt", ""),
        "Finished": state.get("FinishedAt", ""), "Running": str(bool(state.get("Running"))),
        "User": settings.get("User") or "root", "Privileged": str(bool(host.get("Privileged"))),
        "PidMode": host.get("PidMode") or "", "NetworkMode": host.get("NetworkMode") or "",
        "IpcMode": host.get("IpcMode") or "", "CapAdd": ", ".join(cap_add), "SecurityOpt": ", ".join(security_opt),
        "Mounts": "; ".join(f"{m['Source']}:{m['Destination']}{'' if m['RW'] else ':ro'}" for m in mounts),
        "Flag": "; ".join(flags),
    }


def container_techniques(rows: List[Dict[str, str]]) -> List[str]:
    """T1611 when a container could reach its host; T1610 as well when it was also told to run a shell
    or fetch something, which is how such containers are deployed for an escape."""
    techniques = []
    if any(r["Flag"] for r in rows):
        techniques.append("T1611")
        if any(r["Flag"] and re.search(r"\b(?:sh|bash|nsenter|chroot|curl|wget|nc)\b", r["Command"]) for r in rows):
            techniques.append("T1610")
    return techniques


def docker_log_rows(path: str, container: str) -> List[Dict[str, str]]:
    """Docker's json-file log driver: one JSON object per line."""
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            rows.append({"Runtime": "docker", "Container": container[:12], "Pod": "", "Namespace": "",
                         "Stream": entry.get("stream", ""), "LastWriteTime": entry.get("time", ""),
                         "Message": (entry.get("log") or "").rstrip("\n")})
    return rows


CRI_LINE = re.compile(r"^(\S+) (stdout|stderr) [FP] ?(.*)$")


def cri_log_rows(path: str, pod_dir: str, container: str) -> List[Dict[str, str]]:
    """The CRI log format the kubelet writes under /var/log/pods/<namespace>_<pod>_<uid>/<container>/."""
    namespace, _, rest = pod_dir.partition("_")
    pod = rest.rpartition("_")[0] or rest
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            match = CRI_LINE.match(line.rstrip("\n"))
            if match:
                rows.append({"Runtime": "cri", "Container": container, "Pod": pod, "Namespace": namespace,
                             "Stream": match.group(2), "LastWriteTime": match.group(1), "Message": match.group(3)})
    return rows


def container_change_rows(path: str) -> List[Dict[str, str]]:
    """Gandalf's listing of each container's writable layer, flagged where a change is a lead."""
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        flags = []
        inside = row.get("Path", "")
        if row.get("Kind") and TEMP_PATHS.search(inside):
            flags.append("executable in a temporary or hidden path")
        elif row.get("Kind") == "elf":
            flags.append("binary added or changed since the image")
        for pattern, what, _ in PERSISTENCE_FILES:
            if pattern.search(inside):
                flags.append(f"{what} changed")
        row["LastWriteTime"] = _epoch(row.get("MTime") or row.get("LastWriteTime"))
        row["Flag"] = "; ".join(flags)
    return rows


def change_techniques(rows: List[Dict[str, str]]) -> List[str]:
    techniques = set()
    for row in rows:
        if "executable" in row["Flag"] or "binary" in row["Flag"]:
            techniques.add("T1105")
        for pattern, _, technique in PERSISTENCE_FILES:
            if pattern.search(row.get("Path", "")):
                techniques.add(technique)
    return sorted(techniques)


def static_pod_row(path: str, source: str) -> Optional[Dict[str, str]]:
    """A static pod manifest, read without a YAML parser: the fields that matter are one line each."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read(1 << 20)
    if not re.search(r"^kind:\s*Pod\b", text, re.M):
        return None
    name = re.search(r"^\s+name:\s*['\"]?([\w.-]+)", text, re.M)
    namespace = re.search(r"^\s+namespace:\s*['\"]?([\w.-]+)", text, re.M)
    images = re.findall(r"^\s*-?\s*image:\s*['\"]?([^\s'\"]+)", text, re.M)
    command = " ".join(re.findall(r"^\s*-?\s*command:\s*(\[.*\]|.+)$", text, re.M))
    pod = name.group(1) if name else os.path.basename(source)
    flags = []
    if not CONTROL_PLANE_PODS.match(pod):
        flags.append("not a control-plane pod")
    if re.search(r"^\s*privileged:\s*true", text, re.M):
        flags.append("privileged")
    for key, what in (("hostPID", "host PID namespace"), ("hostNetwork", "host network"), ("hostIPC", "host IPC")):
        if re.search(rf"^\s*{key}:\s*true", text, re.M):
            flags.append(what)
    for host_path in re.findall(r"^\s*hostPath:\s*\n\s*path:\s*['\"]?([^\s'\"]+)", text, re.M):
        if _sensitive(host_path) or host_path in DOCKER_SOCKETS:
            flags.append(f"host path {host_path}")
    return {"Source": source, "Name": pod, "Namespace": namespace.group(1) if namespace else "",
            "Images": ", ".join(images), "Command": command, "Flag": "; ".join(flags)}


def static_pod_techniques(rows: List[Dict[str, str]]) -> List[str]:
    """T1543.005 for a static pod Kubernetes didn't put there; T1611 when it can reach the host."""
    techniques = []
    unexpected = [r for r in rows if "not a control-plane pod" in r["Flag"]]
    if unexpected:
        techniques.append("T1543.005")
        if any(r["Flag"] != "not a control-plane pod" for r in unexpected):
            techniques.append("T1611")
    return techniques


def _epoch(seconds) -> str:
    try:
        seconds = int(float(seconds))
        if seconds <= 0:
            return ""
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError, OverflowError, OSError):
        return ""

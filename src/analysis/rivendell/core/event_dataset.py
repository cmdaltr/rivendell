"""Event datasets: archives of Windows events as JSON, with no host.info.

OTRF Security-Datasets (Mordor), the lab's mordor-capture and its converted recordings all ship
events as flat JSON records (one per line, or one array), not as a Gandalf acquisition. Each
host the events name becomes an Elrond host whose events sit in artefacts/cooked/evt/ in the
shape Artemis gives a disk image's .evtx, so ATT&CK tagging, Splunk and Elastic read them the
same way.
"""

import json
import logging
import os
import re
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

logger = logging.getLogger(__name__)

PLATFORM = "Windows"
EVT_DIR = os.path.join("artefacts", "cooked", "evt")
# Flat OTRF fields that belong in the event's System block; the rest is EventData, apart from
# what Winlogbeat/NXLog added in transit, which isn't part of the event.
SYSTEM_FIELDS = {
    "EventID": "EventID", "Channel": "Channel", "Hostname": "Computer", "Computer": "Computer",
    "RecordNumber": "EventRecordID", "EventRecordID": "EventRecordID", "Level": "Level",
    "Task": "Task", "Opcode": "Opcode", "Keywords": "Keywords", "Version": "Version",
}
PROVIDER_FIELDS = ("ProviderName", "SourceName")
TIME_FIELDS = ("@timestamp", "TimeCreated", "EventTime", "timestamp")
TRANSPORT_FIELDS = {
    "@version", "beat_hostname", "host", "tags", "port", "EventReceivedTime", "SourceModuleName",
    "SourceModuleType", "Severity", "SeverityValue", "EventType", "log_name", "source_name",
    "event_data", "user", "agent", "ecs", "log", "input", "fields", "winlog", "event",
}


def _host_name(value: object, fallback: str) -> str:
    """A directory-safe host name: the event's own, else the dataset's."""
    name = re.sub(r"[^A-Za-z0-9._-]", "_", str(value or "").strip()).strip("._")
    return name or fallback


def is_event_record(record: object) -> bool:
    """A Windows event: something with an EventID and a channel or provider."""
    return isinstance(record, dict) and "EventID" in record and any(
        record.get(f) for f in ("Channel", *PROVIDER_FIELDS))


def to_artemis(record: Dict) -> Dict:
    """One flat OTRF record in Artemis's event-log shape (data.Event.System / EventData)."""
    system: Dict = {}
    data: Dict = {}
    timestamp = next((record[f] for f in TIME_FIELDS if record.get(f)), "")
    for key, value in record.items():
        if key in SYSTEM_FIELDS:
            system[SYSTEM_FIELDS[key]] = value
        elif key in PROVIDER_FIELDS:
            system["Provider"] = {"#attributes": {"Name": value}}
        elif key in TIME_FIELDS or key in TRANSPORT_FIELDS:
            continue
        else:
            data[key] = value
    try:
        system["EventID"] = int(system.get("EventID"))
    except (TypeError, ValueError):
        pass
    if timestamp:
        system["TimeCreated"] = {"#attributes": {"SystemTime": timestamp}}
    return {"@timestamp": timestamp, "timestamp": timestamp,
            "data": {"Event": {"System": system, "EventData": data}}}


def read_records(path: str) -> Iterator[Dict]:
    """The records in one JSON file: JSON lines, or a single JSON array."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        head = fh.read(1)
        while head and head.isspace():
            head = fh.read(1)
        fh.seek(0)
        if head == "[":
            try:
                records = json.load(fh)
            except ValueError as e:
                logger.warning("%s isn't valid JSON (%s); skipping it", path, e)
                return
            yield from (r for r in records if isinstance(r, dict))
            return
        for number, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                logger.debug("%s:%d isn't JSON; skipped", path, number)
                continue
            if isinstance(record, dict):
                yield record


def json_files(directory: str) -> List[str]:
    """Every JSON file under an extracted archive, macOS metadata aside."""
    found = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != "__MACOSX"]
        found += [os.path.join(root, f) for f in sorted(files)
                  if f.lower().endswith((".json", ".jsonl", ".ndjson")) and not f.startswith("._")]
    return found


def looks_like_event_dataset(directory: str) -> bool:
    """Whether an extracted archive holds Windows events: its first JSON record is one."""
    for path in json_files(directory):
        for record in read_records(path):
            return is_event_record(record)
    return False


def split_by_host(paths: Iterable[str], fallback: str, out_dir: str) -> Dict[str, Tuple[str, int]]:
    """Convert every event in the files to Artemis's shape, one JSON-lines file per host in
    out_dir (streamed, so a large dataset isn't held in memory). Returns {host: (file, count)}."""
    handles: Dict[str, object] = {}
    counts: Dict[str, int] = {}
    os.makedirs(out_dir, exist_ok=True)
    try:
        for path in paths:
            for record in read_records(path):
                if not is_event_record(record):
                    continue
                host = _host_name(record.get("Hostname") or record.get("Computer"), fallback)
                if host not in handles:
                    handles[host] = open(os.path.join(out_dir, f"{host}.jsonl"), "w", encoding="utf-8")
                    counts[host] = 0
                handles[host].write(json.dumps(to_artemis(record)) + "\n")
                counts[host] += 1
    finally:
        for fh in handles.values():
            fh.close()
    return {h: (os.path.join(out_dir, f"{h}.jsonl"), counts[h]) for h in handles}


def write_json_array(lines_path: str, dest: str) -> None:
    """Rewrite a JSON-lines file as the one JSON array Artemis writes per log, streamed."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(lines_path, encoding="utf-8") as src, open(dest, "w", encoding="utf-8") as out:
        out.write("[")
        for i, line in enumerate(src):
            out.write(("," if i else "") + line.rstrip("\n"))
        out.write("]")


def ingest(staging: str, stem: str, output_directory: str) -> List[Tuple[str, int, str]]:
    """Lay one extracted event dataset out as Elrond hosts.

    Writes <output>/<host>/artefacts/cooked/evt/<stem>.json for every host its events name and
    creates <host>/artefacts/raw/ (empty: there's no disk behind it), so the host is registered
    like any other. Returns [(host, events, evt file)]."""
    split_dir = os.path.join(staging, ".by-host")
    hosts = split_by_host(json_files(staging), _host_name(stem, "dataset"), split_dir)
    placed = []
    for host, (lines_path, count) in sorted(hosts.items()):
        host_dir = os.path.join(output_directory, host)
        os.makedirs(os.path.join(host_dir, "artefacts", "raw"), exist_ok=True)
        dest = os.path.join(host_dir, EVT_DIR, f"{stem}.json")
        write_json_array(lines_path, dest)
        placed.append((host, count, dest))
    return placed


def platform_entry(host: str) -> str:
    """The allimgs value for an event-dataset host: '<host>::Windows'."""
    return f"{host}::{PLATFORM}"


def summary(placed: List[Tuple[str, int, str]]) -> Optional[str]:
    """'3 hosts, 196,071 events' for the audit log."""
    if not placed:
        return None
    events = sum(c for _, c, _ in placed)
    return f"{len(placed)} host{'s' if len(placed) != 1 else ''}, {events:,} events"

"""STIX 2.1 bundles and TAXII 2.1 collections as indicator rows.

Ported from Archer (archer/parsers/stix_import.py and taxii_client.py, MIT,
the same author): parsed from the raw JSON rather than through python-stix2's loaders, because
vendor exports carry custom properties the strict loaders reject.

Archer flattens a bundle into one list of IOCs and one group, which suits generating detections.
Matching evidence needs each indicator's own group and technique, so here an indicator takes them
from its STIX 'indicates' relationships, falling back to the bundle's only intrusion set when it
has exactly one, and never to every technique in the bundle.
"""

import base64
import json
import re
import urllib.request
from typing import Dict, List, Tuple, Union
from urllib.parse import urlencode

from rivendell.threat_intel.schema import Indicator, unique

TECHNIQUE = re.compile(r"\bT\d{4}(?:\.\d{3})?\b")
# objtype(:path)? = 'value': the comparisons inside a STIX pattern
PATTERN_COMPARISON = re.compile(r"([a-z0-9][a-z0-9-]*)(?::([^\s=<>!]+))?\s*(?:=|LIKE|MATCHES)\s*'((?:[^'\\]|\\.)*)'",
                                re.IGNORECASE)
GROUP_TYPES = ("intrusion-set", "threat-actor")
TAXII_ACCEPT = "application/taxii+json;version=2.1"


class IntelFormatError(ValueError):
    """The document isn't the format it was read as."""


def _load(data: Union[str, bytes, dict, list]):
    if isinstance(data, (str, bytes)):
        try:
            return json.loads(data)
        except ValueError as exc:
            raise IntelFormatError(f"not JSON: {exc}") from exc
    return data


def _pattern_values(pattern: str) -> List[Tuple[str, str]]:
    """(kind, value) for each comparison in a STIX pattern."""
    out = []
    for objtype, path, value in PATTERN_COMPARISON.findall(pattern or ""):
        value = value.replace("\\'", "'").replace("\\\\", "\\").strip()
        objtype, path = objtype.lower(), (path or "").lower()
        if not value:
            continue
        if objtype in ("ipv4-addr", "ipv6-addr"):
            out.append(("ip", value))
        elif objtype == "domain-name":
            out.append(("domain", value))
        elif objtype == "url":
            out.append(("url", value))
        elif objtype == "file":
            out.append(("hash" if "hashes" in path else "file", value))
        elif objtype == "process":
            out.append(("cmd" if "command_line" in path else "software", value))
        elif objtype == "windows-registry-key":
            out.append(("reg", value))
        elif objtype == "software":
            out.append(("software", value))
    return out


def _observable_values(obj: Dict) -> List[Tuple[str, str]]:
    kind = obj.get("type")
    if kind in ("ipv4-addr", "ipv6-addr", "domain-name", "url") and obj.get("value"):
        return [({"domain-name": "domain", "url": "url"}.get(kind, "ip"), obj["value"])]
    if kind == "file":
        values = [("hash", h) for h in (obj.get("hashes") or {}).values() if h]
        return values + ([("file", obj["name"])] if obj.get("name") else [])
    if kind == "process" and obj.get("command_line"):
        return [("cmd", obj["command_line"])]
    if kind == "windows-registry-key" and obj.get("key"):
        return [("reg", obj["key"])]
    return []


def _attack_id(obj: Dict) -> str:
    for ref in obj.get("external_references") or []:
        if str(ref.get("source_name", "")).lower() in ("mitre-attack", "mitre attack"):
            if TECHNIQUE.fullmatch(str(ref.get("external_id") or "")):
                return ref["external_id"]
    found = TECHNIQUE.findall(f"{obj.get('name', '')} {obj.get('description') or ''}")
    return found[0] if found else ""


def _reference(obj: Dict) -> str:
    for ref in obj.get("external_references") or []:
        if ref.get("url"):
            return ref["url"]
    return ""


def _tactics(obj: Dict) -> str:
    return ", ".join(p.get("phase_name", "").replace("-", " ").title()
                     for p in obj.get("kill_chain_phases") or [] if p.get("phase_name"))


def parse_stix_bundle(data: Union[str, bytes, dict, list], source: str = "") -> List[Indicator]:
    """A STIX 2.1 bundle (or a bare list of objects) as indicators."""
    data = _load(data)
    objects = data.get("objects") if isinstance(data, dict) else data
    if not isinstance(objects, list):
        raise IntelFormatError("not a STIX bundle: no 'objects' list")
    by_id = {o.get("id"): o for o in objects if isinstance(o, dict) and o.get("id")}
    groups = [o for o in by_id.values() if o.get("type") in GROUP_TYPES]
    only_group = groups[0].get("name", "") if len(groups) == 1 else ""
    report = next((o for o in by_id.values() if o.get("type") == "report"), {})
    source = source or ("STIX: " + (report.get("name") or only_group or (data.get("id", "bundle") if isinstance(data, dict) else "bundle")))
    targets: Dict[str, List[Dict]] = {}
    for rel in by_id.values():
        if rel.get("type") == "relationship" and rel.get("relationship_type") in ("indicates", "related-to", "uses"):
            target = by_id.get(rel.get("target_ref"))
            if target:
                targets.setdefault(rel.get("source_ref"), []).append(target)

    indicators = []
    for obj in by_id.values():
        kind = obj.get("type")
        if kind == "indicator":
            values = _pattern_values(obj.get("pattern", ""))
        elif kind in ("ipv4-addr", "ipv6-addr", "domain-name", "url", "file", "process", "windows-registry-key"):
            values = _observable_values(obj)
        else:
            continue
        linked = targets.get(obj.get("id"), [])
        group = next((t.get("name", "") for t in linked if t.get("type") in GROUP_TYPES), only_group)
        patterns = [t for t in linked if t.get("type") == "attack-pattern"] or [None]
        for pattern in patterns:
            technique = _attack_id(pattern) if pattern else (TECHNIQUE.findall(obj.get("name", "")) or [""])[0]
            for value_kind, value in values:
                indicators.append(Indicator(
                    evidential_element=value, threat_group=group,
                    procedure_example=(obj.get("description") or obj.get("name") or "")[:1000],
                    technique_id=technique, technique_name=(pattern or {}).get("name", ""),
                    tactic=_tactics(pattern or obj),
                    contextual_evidence=f"{value_kind}: {obj.get('name') or kind}"[:500],
                    reference_url=_reference(obj) or _reference(report), source_type=source,
                ))
    return unique(indicators)


def fetch_taxii(collection_url: str, username: str = "", password: str = "", added_after: str = "",
                limit: int = 5000, timeout: int = 60) -> List[Dict]:
    """Every STIX object in a TAXII 2.1 collection, following its pagination. collection_url is the
    collection's base (.../collections/<id>/); added_after (ISO 8601) fetches only what's new."""
    base = collection_url if collection_url.endswith("/") else collection_url + "/"
    headers = {"Accept": TAXII_ACCEPT, "User-Agent": "Rivendell (TAXII 2.1 client)"}
    if username:
        headers["Authorization"] = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()
    params: Dict[str, object] = {"limit": min(limit, 1000)}
    if added_after:
        params["added_after"] = added_after
    objects: List[Dict] = []
    seen = set()
    while len(objects) < limit:
        request = urllib.request.Request(f"{base}objects/?{urlencode(params)}", headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (an analyst-given URL)
            envelope = json.load(response)
        objects.extend(envelope.get("objects") or [])
        following = envelope.get("next")
        if not envelope.get("more") or not following or following in seen:
            break
        seen.add(following)
        params["next"] = following
    return objects[:limit]


def import_taxii(collection_url: str, username: str = "", password: str = "", added_after: str = "",
                 limit: int = 5000) -> List[Indicator]:
    objects = fetch_taxii(collection_url, username, password, added_after, limit)
    return parse_stix_bundle({"type": "bundle", "objects": objects}, source=f"TAXII: {collection_url}")

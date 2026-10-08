#!/usr/bin/env python3 -tt
"""Pre-flight reachability checks for remote SIEM export targets."""
import os
import socket


class SIEMUnavailableError(Exception):
    """Raised when SIEM export is requested but the remote SIEM cannot be reached."""


def _check_reachable(name: str, host: str, port: str, timeout: float) -> None:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            pass
    except (OSError, ValueError) as e:
        raise SIEMUnavailableError(
            f"{name} export requested but {host}:{port} is unreachable ({e}). "
            "If running under Docker Compose, start the SIEM stack with "
            "`docker compose --profile siem up -d`."
        ) from e


def ensure_remote_siem_reachable(splunk: bool, elastic: bool, timeout: float = 5.0) -> None:
    """Fail fast if a requested remote SIEM (SPLUNK_HOST / ELASTICSEARCH_HOST) is not reachable.

    Local installs (host env var unset) are left to the existing SIEMInstaller path.
    Without this, the remote-mode config code swallows connection errors and the
    job reports success with nothing exported.
    """
    if splunk and os.environ.get("SPLUNK_HOST"):
        _check_reachable(
            "Splunk",
            os.environ["SPLUNK_HOST"],
            os.environ.get("SPLUNK_PORT", "8089"),
            timeout,
        )
    if elastic and os.environ.get("ELASTICSEARCH_HOST"):
        _check_reachable(
            "Elasticsearch",
            os.environ["ELASTICSEARCH_HOST"],
            os.environ.get("ELASTICSEARCH_PORT", "9200"),
            timeout,
        )

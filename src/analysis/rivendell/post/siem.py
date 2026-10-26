#!/usr/bin/env python3 -tt
"""Pre-flight reachability checks for remote SIEM export targets."""
import logging
import os
import socket
import time

logger = logging.getLogger(__name__)


class SIEMUnavailableError(Exception):
    """Raised when SIEM export is requested but the remote SIEM cannot be reached."""


# Splunk takes a minute or two to accept connections after its container starts, so
# a refused or timed-out connection is retried; a name that doesn't resolve isn't.
RETRY_DELAYS = (2, 4, 8, 16, 30, 60)


def _check_reachable(name: str, host: str, port: str, timeout: float, delays=RETRY_DELAYS) -> None:
    for attempt, delay in enumerate((*delays, None), 1):
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                return
        except socket.gaierror as e:
            raise SIEMUnavailableError(
                f"{name} export requested but {host} doesn't resolve ({e}): its container isn't "
                "running or isn't on this network. Under Docker Compose, start the SIEM stack with "
                "`docker compose --profile siem up -d`."
            ) from e
        except (OSError, ValueError) as e:
            if isinstance(e, ValueError) or delay is None:
                raise SIEMUnavailableError(
                    f"{name} export requested but {host}:{port} is unreachable after "
                    f"{attempt} attempt{'s' if attempt != 1 else ''} ({e}). If it's still starting, "
                    "re-run once it accepts connections; under Docker Compose, start the SIEM stack "
                    "with `docker compose --profile siem up -d`."
                ) from e
            logger.warning("%s at %s:%s not accepting connections yet (%s); retrying in %ds",
                           name, host, port, e, delay)
            time.sleep(delay)


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

"""SIEM pre-flight: retry while the SIEM starts, fail at once when its name doesn't resolve."""
import socket
import sys
from pathlib import Path

import pytest

# Appended, not prepended: src/analysis/platform would shadow the stdlib module.
sys.path.append(str(Path(__file__).resolve().parents[2] / "src" / "analysis"))

from rivendell.post import siem  # noqa: E402


class Conn:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def connector(outcomes):
    calls = []

    def connect(address, timeout):
        calls.append(address)
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return Conn()
    return connect, calls


def test_refused_is_retried_until_the_siem_accepts(monkeypatch):
    connect, calls = connector([ConnectionRefusedError(), ConnectionRefusedError(), "ok"])
    monkeypatch.setattr(siem.socket, "create_connection", connect)
    monkeypatch.setattr(siem.time, "sleep", lambda _: None)
    siem._check_reachable("Splunk", "splunk", "8089", 1, delays=(1, 1, 1))
    assert len(calls) == 3


def test_dns_failure_is_not_retried(monkeypatch):
    connect, calls = connector([socket.gaierror(-2, "Name or service not known")])
    monkeypatch.setattr(siem.socket, "create_connection", connect)
    with pytest.raises(siem.SIEMUnavailableError, match="doesn't resolve"):
        siem._check_reachable("Splunk", "splunk", "8089", 1, delays=(1, 1))
    assert len(calls) == 1


def test_gives_up_after_the_last_delay(monkeypatch):
    connect, calls = connector([ConnectionRefusedError()] * 3)
    monkeypatch.setattr(siem.socket, "create_connection", connect)
    monkeypatch.setattr(siem.time, "sleep", lambda _: None)
    with pytest.raises(siem.SIEMUnavailableError, match="after 3 attempts"):
        siem._check_reachable("Splunk", "splunk", "8089", 1, delays=(1, 1))

"""Scoped administration of Rivendell's Docker containers and images.

Only resources labelled with the Rivendell compose project and named
``rivendell-*`` are visible or touchable; see ``scope.py``.
"""

from .admin import DockerAdmin
from .engine import Engine, EngineError, EngineUnavailable, candidate_sockets, find_socket
from .scope import BusyError, ScopeError

__all__ = [
    "DockerAdmin",
    "Engine",
    "EngineError",
    "EngineUnavailable",
    "BusyError",
    "ScopeError",
    "candidate_sockets",
    "find_socket",
]

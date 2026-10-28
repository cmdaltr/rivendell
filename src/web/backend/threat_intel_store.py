"""Threat intelligence indicators in Postgres (threat_intel_indicators), for the API and the worker.

Parsing and matching live with Elrond, in rivendell/threat_intel/: the backend mounts that
package (docker-compose.yml) and finds it through elrond_src(), as Mordor's routes find
src/mordor. The worker image has it already, at /opt/elrond-src.
"""

import logging
import os
import sys
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func, or_

try:
    from .storage import ThreatIntelIndicatorModel
except ImportError:
    from storage import ThreatIntelIndicatorModel

logger = logging.getLogger(__name__)

ELROND_SRC = os.environ.get("RIVENDELL_ELROND_SRC", "/opt/elrond-src")
FIELDS = ("evidential_element", "threat_group", "procedure_example", "technique_id", "technique_name", "tactic",
          "contextual_evidence", "reference_url", "navigation_layer_url", "source_type")
INSERT_BATCH = 2000


class ThreatIntelUnavailable(RuntimeError):
    """rivendell/threat_intel isn't importable here."""


def threat_intel():
    """The rivendell.threat_intel package, from Elrond's source tree."""
    if ELROND_SRC not in sys.path:
        sys.path.append(ELROND_SRC)  # appended: /app's modules keep priority
    try:
        import rivendell.threat_intel as package
        import rivendell.threat_intel.match  # noqa: F401 (the worker's export uses the package as a whole)
    except ImportError as exc:
        raise ThreatIntelUnavailable(f"rivendell/threat_intel not found under {ELROND_SRC}: {exc}") from exc
    return package


class ThreatIntelStore:
    """Indicators in the database. Takes a SQLAlchemy session factory (JobStorage.Session)."""

    def __init__(self, session_factory):
        self.Session = session_factory

    def counts(self) -> Dict:
        with self.Session() as session:
            total = session.query(func.count(ThreatIntelIndicatorModel.id)).scalar() or 0
            sources = session.query(ThreatIntelIndicatorModel.source_type, func.count(ThreatIntelIndicatorModel.id)) \
                .group_by(ThreatIntelIndicatorModel.source_type).order_by(ThreatIntelIndicatorModel.source_type).all()
            groups = session.query(func.count(func.distinct(ThreatIntelIndicatorModel.threat_group))) \
                .filter(ThreatIntelIndicatorModel.threat_group != "").scalar() or 0
        return {"total": total, "groups": groups, "sources": [{"source": s or "", "count": n} for s, n in sources]}

    def version(self) -> Tuple[int, int]:
        """(rows, highest id): changes whenever indicators are added or removed."""
        with self.Session() as session:
            return (session.query(func.count(ThreatIntelIndicatorModel.id)).scalar() or 0,
                    session.query(func.max(ThreatIntelIndicatorModel.id)).scalar() or 0)

    def search(self, query: str = "", source: str = "", limit: int = 100, offset: int = 0) -> Dict:
        with self.Session() as session:
            rows = session.query(ThreatIntelIndicatorModel)
            if source:
                rows = rows.filter(ThreatIntelIndicatorModel.source_type == source)
            if query:
                like = f"%{query}%"
                rows = rows.filter(or_(ThreatIntelIndicatorModel.evidential_element.ilike(like),
                                       ThreatIntelIndicatorModel.threat_group.ilike(like),
                                       ThreatIntelIndicatorModel.technique_id.ilike(like)))
            total = rows.count()
            page = rows.order_by(ThreatIntelIndicatorModel.id).offset(offset).limit(min(limit, 500)).all()
            return {"total": total, "indicators": [{"id": r.id, **{f: getattr(r, f) or "" for f in FIELDS}} for r in page]}

    def add(self, indicators: Iterable) -> Tuple[int, int]:
        """(added, already there): an indicator already stored under the same key is skipped."""
        indicators = list(indicators)
        sources = {i.source_type for i in indicators}
        with self.Session() as session:
            existing = set()
            for row in session.query(*[getattr(ThreatIntelIndicatorModel, f) for f in
                                       ("evidential_element", "threat_group", "technique_id", "source_type")]) \
                    .filter(ThreatIntelIndicatorModel.source_type.in_(sources)):
                existing.add(((row[0] or "").lower(), (row[1] or "").lower(), (row[2] or "").upper(), (row[3] or "").lower()))
            new = []
            for indicator in indicators:
                if indicator.key() in existing:
                    continue
                existing.add(indicator.key())
                new.append({f: getattr(indicator, f) for f in FIELDS})
            for start in range(0, len(new), INSERT_BATCH):
                session.bulk_insert_mappings(ThreatIntelIndicatorModel, new[start:start + INSERT_BATCH])
            session.commit()
        return len(new), len(indicators) - len(new)

    def delete_source(self, source: str) -> int:
        with self.Session() as session:
            removed = session.query(ThreatIntelIndicatorModel).filter(ThreatIntelIndicatorModel.source_type == source) \
                .delete(synchronize_session=False)
            session.commit()
        return removed

    def indicators(self) -> List:
        """Every stored indicator, as rivendell.threat_intel Indicators."""
        Indicator = threat_intel().Indicator
        with self.Session() as session:
            return [Indicator(**{f: getattr(r, f) or "" for f in FIELDS})
                    for r in session.query(ThreatIntelIndicatorModel).yield_per(5000)]

    def export_csv(self, path: str) -> int:
        """Every indicator as the CSV Elrond's --threatIntel reads."""
        from rivendell.threat_intel.schema import write_csv  # threat_intel() put it on the path
        return write_csv(path, self.indicators())


_store: Optional[ThreatIntelStore] = None


def configure(storage) -> None:
    """Give the store the backend's JobStorage (main.py does, beside access.configure)."""
    global _store
    _store = ThreatIntelStore(storage.Session)


def store() -> ThreatIntelStore:
    if _store is None:
        raise RuntimeError("threat_intel_store.configure() hasn't been called")
    return _store

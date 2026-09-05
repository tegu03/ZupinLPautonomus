from datetime import datetime, timezone

from zupin.db.models import EvidenceRecord
from zupin.domain import EvidenceStatus
from zupin.evidence import EvidenceRegistry


class FakeScalarResult:
    def __init__(self, rows):
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)


class FakeSession:
    def __init__(self, rows):
        self.rows = rows
        self.added = []

    def scalars(self, _query):
        return FakeScalarResult(self.rows)

    def add(self, record):
        self.added.append(record)

    def flush(self):
        return None


def record(record_id: str, status: str, timestamp: datetime) -> EvidenceRecord:
    return EvidenceRecord(
        id=record_id,
        capability_name="robinhood_lp_write",
        source_reference="fixture",
        evidence_type="fixture",
        retrieved_at=timestamp,
        status=status,
    )


def test_missing_evidence_is_unknown_and_blocked() -> None:
    registry = EvidenceRegistry(FakeSession([]))
    view = registry.resolve("robinhood_lp_write")
    assert view.status is EvidenceStatus.UNKNOWN
    assert registry.execution_allowed(name="robinhood_lp_write", chain_id=4663, protocol="fixture") is False


def test_newest_conflicting_evidence_is_conflicted_and_blocked() -> None:
    timestamp = datetime(2026, 9, 5, tzinfo=timezone.utc)
    registry = EvidenceRegistry(
        FakeSession([
            record("a", "PROVEN", timestamp),
            record("b", "UNKNOWN", timestamp),
        ])
    )
    view = registry.resolve("robinhood_lp_write")
    assert view.status is EvidenceStatus.CONFLICTED
    assert registry.execution_allowed(name="robinhood_lp_write", chain_id=4663, protocol="fixture") is False


def test_newest_proven_evidence_allows_capability() -> None:
    timestamp = datetime(2026, 9, 5, tzinfo=timezone.utc)
    registry = EvidenceRegistry(FakeSession([record("a", "PROVEN", timestamp)]))
    assert registry.execution_allowed(name="robinhood_lp_write", chain_id=4663, protocol="fixture") is True

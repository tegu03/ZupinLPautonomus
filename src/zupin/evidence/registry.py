from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from zupin.domain import EvidenceStatus, IntegrationCapability
from zupin.db.models import EvidenceRecord


@dataclass(frozen=True)
class EvidenceView:
    capability_name: str
    status: EvidenceStatus
    record_ids: tuple[str, ...]


class EvidenceRegistry:
    """Read/write boundary for external capability evidence.

    Missing evidence is UNKNOWN. Conflicting evidence at the newest timestamp
    is CONFLICTED. Neither state is executable.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def record(self, record: EvidenceRecord) -> EvidenceRecord:
        self.session.add(record)
        self.session.flush()
        return record

    def resolve(self, capability_name: str) -> EvidenceView:
        rows = list(
            self.session.scalars(
                select(EvidenceRecord)
                .where(EvidenceRecord.capability_name == capability_name)
                .order_by(EvidenceRecord.retrieved_at.desc(), EvidenceRecord.id.desc())
            )
        )
        if not rows:
            return EvidenceView(capability_name, EvidenceStatus.UNKNOWN, ())

        newest_at = rows[0].retrieved_at
        newest = [row for row in rows if row.retrieved_at == newest_at]
        statuses = {EvidenceStatus(row.status) for row in newest}
        record_ids = tuple(row.id for row in newest)
        if len(statuses) != 1:
            return EvidenceView(capability_name, EvidenceStatus.CONFLICTED, record_ids)
        return EvidenceView(capability_name, next(iter(statuses)), record_ids)

    def capability(self, *, name: str, chain_id: int, protocol: str) -> IntegrationCapability:
        return IntegrationCapability(name, chain_id, protocol, self.resolve(name).status)

    def execution_allowed(self, *, name: str, chain_id: int, protocol: str) -> bool:
        return self.capability(name=name, chain_id=chain_id, protocol=protocol).execution_allowed()


def evidence_status(value: str) -> EvidenceStatus:
    """Normalize persisted evidence status and fail closed on invalid values."""
    try:
        return EvidenceStatus(value)
    except ValueError as exc:
        raise RuntimeError(f"invalid evidence status: {value!r}") from exc

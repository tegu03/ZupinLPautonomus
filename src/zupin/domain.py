from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceStatus(StrEnum):
    PROVEN = "PROVEN"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"


class PositionState(StrEnum):
    INITIALIZING = "INITIALIZING"
    SCANNING = "SCANNING"
    EVALUATING = "EVALUATING"
    READY = "READY"
    DEPLOYING = "DEPLOYING"
    MONITORING = "MONITORING"
    REBALANCING = "REBALANCING"
    HARVESTING = "HARVESTING"
    COMPOUNDING = "COMPOUNDING"
    EXITING = "EXITING"
    RECONCILING = "RECONCILING"
    CLOSED = "CLOSED"
    PAUSED = "PAUSED"
    EMERGENCY = "EMERGENCY"


ACTIVE_POSITION_STATES = frozenset(
    {
        PositionState.DEPLOYING,
        PositionState.MONITORING,
        PositionState.REBALANCING,
        PositionState.HARVESTING,
        PositionState.COMPOUNDING,
        PositionState.EXITING,
        PositionState.RECONCILING,
    }
)


@dataclass(frozen=True, slots=True)
class IntegrationCapability:
    name: str
    chain_id: int
    protocol: str
    evidence: EvidenceStatus

    def execution_allowed(self) -> bool:
        return self.evidence is EvidenceStatus.PROVEN


@dataclass(frozen=True, slots=True)
class Position:
    user_id: str
    position_id: str
    state: PositionState


def assert_one_active_position(positions: list[Position]) -> None:
    active = [p for p in positions if p.state in ACTIVE_POSITION_STATES]
    if len(active) > 1:
        raise ValueError("one-active-position invariant violated")


def assert_execution_evidence(capability: IntegrationCapability) -> None:
    if not capability.execution_allowed():
        raise RuntimeError(
            f"execution blocked: capability evidence is {capability.evidence.value}"
        )

import pytest

from zupin.domain import (
    EvidenceStatus,
    IntegrationCapability,
    Position,
    PositionState,
    assert_execution_evidence,
    assert_one_active_position,
)


def test_unknown_capability_is_not_executable() -> None:
    capability = IntegrationCapability("lp_write", 4663, "unknown", EvidenceStatus.UNKNOWN)
    with pytest.raises(RuntimeError, match="UNKNOWN"):
        assert_execution_evidence(capability)


def test_conflicted_capability_is_not_executable() -> None:
    capability = IntegrationCapability("lp_write", 4663, "unknown", EvidenceStatus.CONFLICTED)
    with pytest.raises(RuntimeError, match="CONFLICTED"):
        assert_execution_evidence(capability)


def test_proven_capability_is_executable_by_evidence_gate() -> None:
    capability = IntegrationCapability("lp_read", 4663, "verified", EvidenceStatus.PROVEN)
    assert_execution_evidence(capability)


def test_one_active_position_invariant() -> None:
    positions = [
        Position("u1", "p1", PositionState.MONITORING),
        Position("u1", "p2", PositionState.CLOSED),
    ]
    assert_one_active_position(positions)


def test_multiple_active_positions_fail_closed() -> None:
    positions = [
        Position("u1", "p1", PositionState.MONITORING),
        Position("u1", "p2", PositionState.EXITING),
    ]
    with pytest.raises(ValueError, match="one-active-position"):
        assert_one_active_position(positions)

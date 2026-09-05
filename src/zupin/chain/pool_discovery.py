"""Fail-closed, read-only Uniswap v4 pool metadata discovery.

Pool metadata is treated as external evidence. This module does not query a
DEX, sign transactions, or construct write calldata. It validates a supplied
PoolKey and rejects missing or conflicting observations instead of guessing.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


ZERO_ADDRESS = "0x" + "0" * 40


class PoolMetadataError(ValueError):
    """Raised when supplied pool metadata is structurally invalid."""


@dataclass(frozen=True)
class PoolKey:
    token0: str
    token1: str
    fee: int
    tick_spacing: int
    hook: str


@dataclass(frozen=True)
class PoolObservation:
    pool_key: PoolKey
    observed_at: datetime
    source_ref: str
    evidence_status: str = "PROVEN"
    pool_id: str | None = None


@dataclass(frozen=True)
class PoolDiscoveryResult:
    status: str
    pool: PoolObservation | None
    reason: str


def _is_address(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 42 or not value.startswith("0x"):
        return False
    try:
        int(value[2:], 16)
    except ValueError:
        return False
    return True


def _is_bytes32(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 66 or not value.startswith("0x"):
        return False
    try:
        int(value[2:], 16)
    except ValueError:
        return False
    return True


def validate_pool_key(pool_key: PoolKey) -> None:
    """Validate the structural invariants required for a Uniswap v4 PoolKey."""
    if not _is_address(pool_key.token0) or not _is_address(pool_key.token1):
        raise PoolMetadataError("token addresses are malformed")
    if pool_key.token0.lower() == pool_key.token1.lower():
        raise PoolMetadataError("token0 and token1 must differ")
    # Uniswap v4 PoolKey requires currencies to be sorted by address.
    if int(pool_key.token0[2:], 16) >= int(pool_key.token1[2:], 16):
        raise PoolMetadataError("token0 must sort before token1")
    if not isinstance(pool_key.fee, int) or not 0 <= pool_key.fee <= 0xFFFFFF:
        raise PoolMetadataError("fee must be an unsigned 24-bit integer")
    if not isinstance(pool_key.tick_spacing, int) or not -(2**23) <= pool_key.tick_spacing < 2**23:
        raise PoolMetadataError("tick_spacing must fit int24")
    if not _is_address(pool_key.hook):
        raise PoolMetadataError("hook address is malformed")


def _observation_key(observation: PoolObservation) -> tuple[str, str, int, int, str]:
    key = observation.pool_key
    return (
        key.token0.lower(),
        key.token1.lower(),
        key.fee,
        key.tick_spacing,
        key.hook.lower(),
    )


def discover_pool(observations: Iterable[PoolObservation]) -> PoolDiscoveryResult:
    """Resolve the newest validated pool observation, failing closed on conflict.

    Only ``PROVEN`` observations are executable evidence. If the newest
    timestamp contains more than one distinct PoolKey, the result is
    ``CONFLICTED``. Missing observations or non-proven evidence return
    ``UNKNOWN``.
    """
    items = list(observations)
    if not items:
        return PoolDiscoveryResult("UNKNOWN", None, "no pool observations supplied")

    try:
        for item in items:
            validate_pool_key(item.pool_key)
            if not item.source_ref:
                raise PoolMetadataError("source_ref is required")
            if item.pool_id is not None and not _is_bytes32(item.pool_id):
                raise PoolMetadataError("pool_id must be bytes32")
    except PoolMetadataError as exc:
        return PoolDiscoveryResult("UNKNOWN", None, str(exc))

    latest_at = max(item.observed_at for item in items)
    latest = [item for item in items if item.observed_at == latest_at]
    proven = [item for item in latest if item.evidence_status == "PROVEN"]
    if not proven:
        statuses = sorted({item.evidence_status for item in latest})
        return PoolDiscoveryResult("UNKNOWN", None, f"latest pool evidence is not PROVEN: {statuses}")

    keys = {_observation_key(item) for item in proven}
    if len(keys) != 1:
        return PoolDiscoveryResult("CONFLICTED", None, "latest PROVEN observations disagree on PoolKey")

    selected = sorted(proven, key=lambda item: (item.source_ref, item.pool_id or ""))[0]
    return PoolDiscoveryResult("PROVEN", selected, "latest validated PROVEN PoolKey is consistent")

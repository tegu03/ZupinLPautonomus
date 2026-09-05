"""Fail-closed validation of read-only Uniswap v4 pool state observations."""
from __future__ import annotations

from dataclasses import dataclass

from .pool_discovery import PoolObservation, validate_pool_key


@dataclass(frozen=True)
class PoolStateObservation:
    pool_id: str
    sqrt_price_x96: int
    tick: int
    protocol_fee: int
    lp_fee: int
    active_liquidity: int
    observed_block: int
    source_ref: str
    evidence_status: str = "PROVEN"


@dataclass(frozen=True)
class PoolStateVerification:
    status: str
    reason: str


def verify_pool_state(pool: PoolObservation, state: PoolStateObservation) -> PoolStateVerification:
    """Verify a state snapshot is structurally compatible with a discovered PoolKey.

    This is deliberately a pure validator. It does not perform RPC calls and does
    not promote a pool to executable capability. StateView exposes getSlot0 and
    getLiquidity as read-only views over the v4 PoolManager state.
    """
    if pool.evidence_status != "PROVEN":
        return PoolStateVerification("UNKNOWN", "pool metadata evidence is not PROVEN")
    if state.evidence_status != "PROVEN":
        return PoolStateVerification("UNKNOWN", "pool state evidence is not PROVEN")
    try:
        validate_pool_key(pool.pool_key)
    except ValueError as exc:
        return PoolStateVerification("UNKNOWN", str(exc))
    if not pool.pool_id or pool.pool_id.lower() != state.pool_id.lower():
        return PoolStateVerification("CONFLICTED", "pool ID does not match state observation")
    if not state.source_ref:
        return PoolStateVerification("UNKNOWN", "state source_ref is required")
    if state.observed_block < 0:
        return PoolStateVerification("UNKNOWN", "observed_block must be non-negative")
    if state.sqrt_price_x96 <= 0:
        return PoolStateVerification("UNKNOWN", "pool is not initialized: sqrtPriceX96 is zero")
    if not -(2**23) <= state.tick < 2**23:
        return PoolStateVerification("UNKNOWN", "tick must fit int24")
    if not 0 <= state.protocol_fee <= 0xFFFFFF:
        return PoolStateVerification("UNKNOWN", "protocol_fee must fit uint24")
    if state.lp_fee != pool.pool_key.fee:
        return PoolStateVerification("CONFLICTED", "live lp_fee does not match PoolKey fee")
    if state.active_liquidity < 0:
        return PoolStateVerification("UNKNOWN", "active liquidity must be non-negative")
    return PoolStateVerification("PROVEN", "pool metadata and read-only state snapshot are consistent")

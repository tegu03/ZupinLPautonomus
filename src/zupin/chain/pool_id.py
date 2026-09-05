"""Deterministic Uniswap v4 PoolId derivation.

PoolId is keccak256(abi.encode(PoolKey)). This module is pure: it performs no
RPC calls and has no transaction/signing capability.
"""
from __future__ import annotations

from eth_hash.auto import keccak

from .pool_discovery import PoolKey, validate_pool_key


def derive_pool_id(pool_key: PoolKey) -> str:
    """Derive the canonical bytes32 PoolId from a validated PoolKey."""
    validate_pool_key(pool_key)
    encoded = b"".join(
        (
            int(pool_key.token0[2:], 16).to_bytes(32, "big"),
            int(pool_key.token1[2:], 16).to_bytes(32, "big"),
            pool_key.fee.to_bytes(32, "big"),
            pool_key.tick_spacing.to_bytes(32, "big", signed=True),
            int(pool_key.hook[2:], 16).to_bytes(32, "big"),
        )
    )
    return "0x" + keccak(encoded).hex()

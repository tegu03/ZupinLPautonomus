"""Packed V4 PositionInfo decoder, matching Uniswap PositionInfoLibrary."""

from __future__ import annotations

from dataclasses import dataclass

_MASK_24 = (1 << 24) - 1
_MASK_POOL_200 = ((1 << 200) - 1) << 56


def _sign_extend_24(value: int) -> int:
    value &= _MASK_24
    return value - (1 << 24) if value & (1 << 23) else value


@dataclass(frozen=True)
class PositionInfo:
    raw: int
    pool_id_truncated: bytes
    tick_lower: int
    tick_upper: int
    has_subscriber: bool

    @classmethod
    def decode(cls, raw: int) -> "PositionInfo":
        if raw < 0 or raw >= 1 << 256:
            raise ValueError("PositionInfo must be a uint256")
        pool_int = raw & _MASK_POOL_200
        pool_id = pool_int.to_bytes(32, "big")[:25]
        return cls(raw, pool_id, _sign_extend_24(raw >> 8), _sign_extend_24(raw >> 32), bool(raw & 0xFF))


def decode_position_info(raw: int) -> PositionInfo:
    return PositionInfo.decode(raw)

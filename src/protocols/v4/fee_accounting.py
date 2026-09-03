"""Deterministic Uniswap V4 position-level fee accounting.

Pool-wide volume * fee is only an opportunity signal. This module converts
V4 fee-growth-inside checkpoints into position-attributable token fees.
It is read-only math: collection and execution remain outside this module.
"""

from __future__ import annotations

from dataclasses import dataclass

Q128 = 1 << 128
UINT256 = 1 << 256


def fee_growth_delta_x128(current: int, entry: int) -> int:
    """Return uint256-wrapped fee-growth delta."""
    if not 0 <= current < UINT256 or not 0 <= entry < UINT256:
        raise ValueError("fee growth values must be uint256")
    return (current - entry) % UINT256


def fees_from_growth(liquidity: int, growth_delta_x128: int) -> int:
    """Convert Q128 fee growth into whole token base units."""
    if liquidity < 0:
        raise ValueError("liquidity must be non-negative")
    if not 0 <= growth_delta_x128 < UINT256:
        raise ValueError("growth delta must be uint256")
    return (liquidity * growth_delta_x128) // Q128


@dataclass(frozen=True)
class V4FeeGrowthCheckpoint:
    token0_x128: int
    token1_x128: int
    liquidity: int

    def validate(self) -> None:
        if not 0 <= self.token0_x128 < UINT256 or not 0 <= self.token1_x128 < UINT256:
            raise ValueError("checkpoint fee growth must be uint256")
        if self.liquidity < 0:
            raise ValueError("liquidity must be non-negative")


@dataclass(frozen=True)
class V4FeeAccrual:
    growth_delta_token0_x128: int
    growth_delta_token1_x128: int
    gross_token0: int
    gross_token1: int
    collected_token0: int = 0
    collected_token1: int = 0

    @property
    def uncollected_token0(self) -> int:
        return max(0, self.gross_token0 - self.collected_token0)

    @property
    def uncollected_token1(self) -> int:
        return max(0, self.gross_token1 - self.collected_token1)


def accrue_from_checkpoints(
    entry: V4FeeGrowthCheckpoint,
    current: V4FeeGrowthCheckpoint,
    collected_token0: int = 0,
    collected_token1: int = 0,
) -> V4FeeAccrual:
    """Calculate gross and uncollected fees for one fixed-liquidity lifecycle."""
    entry.validate()
    current.validate()
    if current.liquidity != entry.liquidity:
        raise ValueError("liquidity changed; use piecewise checkpoints")
    if collected_token0 < 0 or collected_token1 < 0:
        raise ValueError("collected fees must be non-negative")

    d0 = fee_growth_delta_x128(current.token0_x128, entry.token0_x128)
    d1 = fee_growth_delta_x128(current.token1_x128, entry.token1_x128)
    g0 = fees_from_growth(current.liquidity, d0)
    g1 = fees_from_growth(current.liquidity, d1)
    return V4FeeAccrual(d0, d1, g0, g1, collected_token0, collected_token1)


def position_fee_checkpoint(
    fee_growth_inside_token0_x128: int,
    fee_growth_inside_token1_x128: int,
    liquidity: int,
) -> V4FeeGrowthCheckpoint:
    """Build a validated checkpoint directly from StateView fee-growth-inside."""
    checkpoint = V4FeeGrowthCheckpoint(
        fee_growth_inside_token0_x128,
        fee_growth_inside_token1_x128,
        liquidity,
    )
    checkpoint.validate()
    return checkpoint

from pytest import raises

from src.protocols.v4.fee_accounting import (
    Q128,
    UINT256,
    V4FeeGrowthCheckpoint,
    accrue_from_checkpoints,
    fee_growth_delta_x128,
    fees_from_growth,
    position_fee_checkpoint,
)


def test_fee_growth_delta_is_q128_and_wrap_safe() -> None:
    assert fee_growth_delta_x128(10, 4) == 6
    assert fee_growth_delta_x128(2, UINT256 - 3) == 5


def test_fees_from_growth_converts_per_liquidity_growth() -> None:
    assert fees_from_growth(100, 2 * Q128) == 200


def test_position_accrual_tracks_gross_and_uncollected() -> None:
    entry = position_fee_checkpoint(Q128, 2 * Q128, 100)
    current = position_fee_checkpoint(3 * Q128, 5 * Q128, 100)
    accrual = accrue_from_checkpoints(entry, current, collected_token0=25, collected_token1=50)

    assert accrual.gross_token0 == 200
    assert accrual.gross_token1 == 300
    assert accrual.uncollected_token0 == 175
    assert accrual.uncollected_token1 == 250


def test_liquidity_change_requires_piecewise_accounting() -> None:
    entry = V4FeeGrowthCheckpoint(Q128, Q128, 100)
    current = V4FeeGrowthCheckpoint(2 * Q128, 2 * Q128, 101)
    with raises(ValueError, match="liquidity changed"):
        accrue_from_checkpoints(entry, current)


def test_invalid_growth_is_rejected() -> None:
    with raises(ValueError):
        fee_growth_delta_x128(UINT256, 0)
    with raises(ValueError):
        fees_from_growth(1, UINT256)

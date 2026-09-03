from decimal import Decimal as D

from src.strategy.farming_intelligence import (
    PoolOpportunity,
    RangeCandidate,
    decide_entry,
    rebalance_is_economic,
    score_pool,
)


def test_hotdog_eth_is_high_opportunity_but_not_automatic_entry() -> None:
    pool = PoolOpportunity(
        pool_id="HOTDOG/ETH-V4-0.90",
        fee_rate=D("0.009"),
        tvl_usd=D("31800"),
        volume_24h_usd=D("2920000"),
    )
    assert pool.volume_tvl_ratio > D("90")
    assert pool.gross_pool_fee_24h_usd == D("26280")
    assert score_pool(pool) > D("0")


def test_gas_is_transaction_cost_not_swap_fee() -> None:
    pool = PoolOpportunity("test", D("0.009"), D("31800"), D("2920000"))
    candidate = RangeCandidate(D("-5"), D("5"), D("0.8"), D("0.02"))
    decision = decide_entry(pool, [candidate], D("100"), D("1"), D("1"), 4, D("0"))
    assert decision.lifecycle_gas_usd == D("4")
    assert decision.expected_fee_usd > D("0")


def test_rebalance_is_rejected_when_incremental_fee_does_not_cover_gas() -> None:
    assert not rebalance_is_economic(D("1.2"), D("0"), D("0"), D("1"), D("0.5"), D("0"))


def test_rebalance_is_accepted_when_incremental_fee_clears_all_costs() -> None:
    assert rebalance_is_economic(D("8"), D("0.5"), D("0.25"), D("1"), D("1"), D("2"))


def test_wider_range_can_win_when_active_fraction_is_higher() -> None:
    pool = PoolOpportunity("test", D("0.009"), D("31800"), D("2920000"))
    tight = RangeCandidate(D("-2"), D("2"), D("0.30"), D("0.08"), D("0"))
    wide = RangeCandidate(D("-8"), D("8"), D("0.90"), D("0.035"), D("0"))
    decision = decide_entry(pool, [tight, wide], D("100"), D("1"), D("1"), 2, D("0"))
    assert (decision.range_lower_pct, decision.range_upper_pct) == (D("-8"), D("8"))

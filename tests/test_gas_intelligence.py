from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.infrastructure.gas_intelligence import (
    GasIntelligence,
    GasObservation,
    GasState,
    entry_allowed,
)


NOW = datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)


def obs(cost_usd: str, minutes_ago: int = 0) -> GasObservation:
    # 100,000 gas at 1 native = $3000 => 1 gwei costs $0.30.
    # Choose max fee so the resulting transaction cost equals cost_usd.
    cost = Decimal(cost_usd)
    gas_limit = 100_000
    native_usd = Decimal("3000")
    max_fee_wei = int(cost * Decimal(10**18) / (Decimal(gas_limit) * native_usd))
    return GasObservation(
        observed_at=NOW - timedelta(minutes=minutes_ago),
        gas_limit=gas_limit,
        max_fee_per_gas_wei=max_fee_wei,
        native_usd=native_usd,
    )


def test_cost_calculation():
    assert obs("1.30").projected_cost_usd() == Decimal("1.30")


def test_above_130_blocks_new_entries():
    intelligence = GasIntelligence(hard_cap_usd=Decimal("1.30"))
    assessment = intelligence.assess(obs("1.31"), [obs("1.10", 2)], now=NOW)
    assert assessment.state is GasState.BLOCKED
    assert not entry_allowed(assessment)


def test_at_cap_is_allowed_but_not_stable_without_history():
    intelligence = GasIntelligence(hard_cap_usd=Decimal("1.30"), minimum_samples=3)
    assessment = intelligence.assess(obs("1.30"), [obs("1.20", 2)], now=NOW)
    assert assessment.state is GasState.ELEVATED
    assert entry_allowed(assessment)


def test_stale_observation_fails_closed():
    intelligence = GasIntelligence(stale_after=timedelta(minutes=5))
    assessment = intelligence.assess(obs("1.00", 10), now=NOW)
    assert assessment.state is GasState.UNKNOWN
    assert not entry_allowed(assessment)


def test_rolling_history_can_classify_stable():
    intelligence = GasIntelligence(minimum_samples=3, elevated_multiple=Decimal("1.10"))
    history = [obs("1.00", 10), obs("1.05", 5)]
    assessment = intelligence.assess(obs("1.04"), history, now=NOW)
    assert assessment.state is GasState.STABLE
    assert assessment.rolling_median_cost_usd is not None


def test_future_timestamp_fails_closed():
    intelligence = GasIntelligence()
    future = GasObservation(
        observed_at=NOW + timedelta(minutes=1),
        gas_limit=100_000,
        max_fee_per_gas_wei=100_000_000,
        native_usd=Decimal("3000"),
    )
    assessment = intelligence.assess(future, now=NOW)
    assert assessment.state is GasState.UNKNOWN
    assert not entry_allowed(assessment)


def test_invalid_native_price_fails_closed():
    intelligence = GasIntelligence()
    bad = GasObservation(
        observed_at=NOW,
        gas_limit=100_000,
        max_fee_per_gas_wei=100_000_000,
        native_usd=Decimal("0"),
    )
    assessment = intelligence.assess(bad, now=NOW)
    assert assessment.state is GasState.UNKNOWN
    assert not entry_allowed(assessment)

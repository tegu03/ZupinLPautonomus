"""Deterministic fee-farming intelligence for Robinhood Chain LP decisions.

This module is deliberately protocol-agnostic at the strategy boundary. Protocol
readers provide observed pool/range state; this module converts that state into
an auditable opportunity estimate. It never signs or broadcasts transactions.

Important: pool-wide volume is only an opportunity signal. Position-level fee
capture must come from the V3/V4 fee-growth/accounting adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from math import sqrt

D = Decimal


class MarketRegime(str, Enum):
    RANGE_BOUND = "range_bound"
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    HIGH_VOLATILITY = "high_volatility"


@dataclass(frozen=True)
class PoolOpportunity:
    pool_id: str
    fee_rate: Decimal
    tvl_usd: Decimal
    volume_24h_usd: Decimal
    security_pass: bool = True

    @property
    def volume_tvl_ratio(self) -> Decimal:
        if self.tvl_usd <= 0:
            return D(0)
        return self.volume_24h_usd / self.tvl_usd

    @property
    def gross_pool_fee_24h_usd(self) -> Decimal:
        if self.volume_24h_usd <= 0 or self.fee_rate <= 0:
            return D(0)
        return self.volume_24h_usd * self.fee_rate


@dataclass(frozen=True)
class RangeCandidate:
    lower_pct: Decimal
    upper_pct: Decimal
    expected_active_fraction: Decimal
    expected_fee_capture_fraction: Decimal
    expected_il_usd: Decimal = D(0)
    expected_slippage_usd: Decimal = D(0)

    @property
    def width_pct(self) -> Decimal:
        return self.upper_pct - self.lower_pct


@dataclass(frozen=True)
class FarmingDecision:
    action: str
    score: Decimal
    expected_fee_usd: Decimal
    lifecycle_gas_usd: Decimal
    expected_net_usd: Decimal
    range_lower_pct: Decimal | None
    range_upper_pct: Decimal | None
    reason: str


def score_pool(opportunity: PoolOpportunity) -> Decimal:
    """Return a bounded opportunity score from pool-level observations.

    The score is intentionally not a profitability prediction. It rewards fee
    density and volume/TVL while penalizing thin TVL. Security failure is a
    hard rejection represented by zero.
    """
    if not opportunity.security_pass:
        return D(0)
    if opportunity.tvl_usd <= 0 or opportunity.volume_24h_usd <= 0:
        return D(0)

    density = opportunity.gross_pool_fee_24h_usd / opportunity.tvl_usd
    # sqrt prevents an extreme volume/TVL outlier from dominating every other
    # signal while retaining strong preference for active pools.
    raw = sqrt(float(max(density, D(0)))) * min(float(opportunity.fee_rate * D(100)), 10.0)
    return min(D(100), D(str(raw * 10)))


def evaluate_range(
    opportunity: PoolOpportunity,
    candidate: RangeCandidate,
    capital_usd: Decimal,
    horizon_days: Decimal,
    gas_per_tx_usd: Decimal,
    planned_tx_count: int,
    risk_buffer_usd: Decimal = D(0),
) -> Decimal:
    """Estimate net result for one range candidate.

    Fee capture is explicitly supplied by the range model. We do not pretend
    that pool-wide fees are automatically earned by an LP position.
    """
    if capital_usd <= 0 or horizon_days <= 0:
        return D("-Infinity")
    if not D(0) <= candidate.expected_active_fraction <= D(1):
        return D("-Infinity")
    if not D(0) <= candidate.expected_fee_capture_fraction <= D(1):
        return D("-Infinity")
    if gas_per_tx_usd < 0 or planned_tx_count < 0:
        return D("-Infinity")

    gross_pool_fee = opportunity.gross_pool_fee_24h_usd * horizon_days
    fee = gross_pool_fee * candidate.expected_active_fraction * candidate.expected_fee_capture_fraction
    gas = gas_per_tx_usd * D(planned_tx_count)
    return fee - candidate.expected_il_usd - candidate.expected_slippage_usd - gas - risk_buffer_usd


def choose_range(
    opportunity: PoolOpportunity,
    candidates: list[RangeCandidate],
    capital_usd: Decimal,
    horizon_days: Decimal,
    gas_per_tx_usd: Decimal,
    planned_tx_count: int,
    risk_buffer_usd: Decimal = D(0),
) -> tuple[RangeCandidate | None, Decimal]:
    if not candidates:
        return None, D("-Infinity")
    ranked = [
        (c, evaluate_range(opportunity, c, capital_usd, horizon_days, gas_per_tx_usd, planned_tx_count, risk_buffer_usd))
        for c in candidates
    ]
    return max(ranked, key=lambda item: item[1])


def rebalance_is_economic(
    expected_additional_fee_usd: Decimal,
    expected_il_change_usd: Decimal,
    expected_slippage_usd: Decimal,
    gas_usd: Decimal,
    risk_buffer_usd: Decimal,
    minimum_net_benefit_usd: Decimal,
) -> bool:
    """Only rebalance when incremental benefit clears all incremental costs."""
    benefit = expected_additional_fee_usd - expected_il_change_usd - expected_slippage_usd
    return benefit - gas_usd - risk_buffer_usd > minimum_net_benefit_usd


def decide_entry(
    opportunity: PoolOpportunity,
    candidates: list[RangeCandidate],
    capital_usd: Decimal,
    horizon_days: Decimal,
    gas_per_tx_usd: Decimal,
    lifecycle_tx_count: int,
    minimum_net_profit_usd: Decimal,
    risk_buffer_usd: Decimal = D(0),
) -> FarmingDecision:
    """Select ENTER only when a range clears the complete economic gate."""
    if not opportunity.security_pass:
        return FarmingDecision("REJECT", D(0), D(0), D(0), D("-Infinity"), None, None, "security gate failed")
    if gas_per_tx_usd < 0 or lifecycle_tx_count < 0:
        return FarmingDecision("REJECT", D(0), D(0), D(0), D("-Infinity"), None, None, "invalid gas inputs")

    chosen, net = choose_range(
        opportunity, candidates, capital_usd, horizon_days, gas_per_tx_usd, lifecycle_tx_count, risk_buffer_usd
    )
    if chosen is None:
        return FarmingDecision("WAIT", score_pool(opportunity), D(0), D(0), D("-Infinity"), None, None, "no valid range")

    gas = gas_per_tx_usd * D(lifecycle_tx_count)
    gross = opportunity.gross_pool_fee_24h_usd * horizon_days
    fee = gross * chosen.expected_active_fraction * chosen.expected_fee_capture_fraction
    action = "ENTER" if net > minimum_net_profit_usd else "WAIT"
    reason = "best risk-adjusted range clears economic gate" if action == "ENTER" else "fee opportunity does not clear lifecycle costs"
    return FarmingDecision(action, score_pool(opportunity), fee, gas, net, chosen.lower_pct, chosen.upper_pct, reason)

"""Gas intelligence for autonomous LP decisions on Robinhood Chain.

This module is deliberately deterministic and side-effect free.  It does not
query an RPC and it never sends transactions.  An RPC/market adapter can feed
it fresh observations later.

Policy:
- $1.30 is a hard per-transaction gas cap for NEW LP entries.
- stale, incomplete, or unverifiable gas inputs fail closed;
- existing positions are not forced to exit merely because gas is expensive;
- rolling observations are used to avoid treating a single spike as the
  normal gas regime.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Iterable, Sequence


D = Decimal
WEI_PER_NATIVE = D(10) ** 18


class GasState(str, Enum):
    """Decision state for new LP entries."""

    STABLE = "GAS_STABLE"
    ELEVATED = "GAS_ELEVATED"
    BLOCKED = "GAS_BLOCKED"
    UNKNOWN = "GAS_UNKNOWN"


@dataclass(frozen=True)
class GasObservation:
    """One transaction-cost observation at a specific time."""

    observed_at: datetime
    gas_limit: int
    max_fee_per_gas_wei: int
    native_usd: D

    def projected_cost_usd(self) -> D:
        if self.gas_limit <= 0 or self.max_fee_per_gas_wei < 0:
            raise ValueError("invalid gas observation")
        if self.native_usd <= 0:
            raise ValueError("native_usd must be positive")
        return (
            D(self.gas_limit)
            * D(self.max_fee_per_gas_wei)
            / WEI_PER_NATIVE
            * self.native_usd
        )


@dataclass(frozen=True)
class GasAssessment:
    state: GasState
    projected_cost_usd: D | None
    rolling_median_cost_usd: D | None
    sample_count: int
    fresh: bool
    reason: str

    @property
    def allow_new_entry(self) -> bool:
        """Only a fresh, known cost at/below the hard cap may enter."""
        return self.state in {GasState.STABLE, GasState.ELEVATED}


class GasIntelligence:
    """Rolling gas assessor with a hard entry cap and fail-closed behavior."""

    def __init__(
        self,
        *,
        hard_cap_usd: D = D("1.30"),
        stale_after: timedelta = timedelta(minutes=5),
        window: timedelta = timedelta(minutes=30),
        elevated_multiple: D = D("1.10"),
        minimum_samples: int = 3,
    ) -> None:
        if hard_cap_usd <= 0:
            raise ValueError("hard_cap_usd must be positive")
        if stale_after <= timedelta(0) or window <= timedelta(0):
            raise ValueError("time windows must be positive")
        if elevated_multiple < D("1"):
            raise ValueError("elevated_multiple must be >= 1")
        if minimum_samples < 1:
            raise ValueError("minimum_samples must be >= 1")
        self.hard_cap_usd = hard_cap_usd
        self.stale_after = stale_after
        self.window = window
        self.elevated_multiple = elevated_multiple
        self.minimum_samples = minimum_samples

    def assess(
        self,
        current: GasObservation | None,
        history: Sequence[GasObservation] = (),
        *,
        now: datetime | None = None,
    ) -> GasAssessment:
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        if current is None:
            return GasAssessment(GasState.UNKNOWN, None, None, 0, False, "missing gas observation")

        try:
            current_cost = current.projected_cost_usd()
        except (ValueError, InvalidOperation):
            return GasAssessment(GasState.UNKNOWN, None, None, 0, False, "invalid gas observation")

        age = now - self._aware(current.observed_at)
        fresh = timedelta(0) <= age <= self.stale_after
        if not fresh:
            return GasAssessment(
                GasState.UNKNOWN,
                current_cost,
                None,
                0,
                False,
                "gas observation is stale or from the future",
            )

        cutoff = now - self.window
        costs = [
            self._safe_cost(item)
            for item in history
            if cutoff <= self._aware(item.observed_at) <= now
        ]
        costs = [cost for cost in costs if cost is not None]
        if current_cost not in costs:
            costs.append(current_cost)
        costs.sort()
        median = costs[len(costs) // 2]

        if current_cost > self.hard_cap_usd:
            return GasAssessment(
                GasState.BLOCKED, current_cost, median, len(costs), True,
                "projected gas cost exceeds hard entry cap",
            )

        # With insufficient history, remain conservative but allow an entry
        # when the actual transaction estimate is below the hard cap.  This is
        # not a profitability approval; the economic gate remains authoritative.
        if len(costs) < self.minimum_samples:
            return GasAssessment(
                GasState.ELEVATED, current_cost, median, len(costs), True,
                "fresh cost below cap but rolling history is incomplete",
            )

        elevated_threshold = min(self.hard_cap_usd, median * self.elevated_multiple)
        state = GasState.ELEVATED if current_cost > elevated_threshold else GasState.STABLE
        return GasAssessment(
            state, current_cost, median, len(costs), True,
            "fresh gas cost within hard cap",
        )

    @staticmethod
    def _aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("observation timestamps must be timezone-aware")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _safe_cost(observation: GasObservation) -> D | None:
        try:
            return observation.projected_cost_usd()
        except (ValueError, InvalidOperation):
            return None


def entry_allowed(assessment: GasAssessment) -> bool:
    """Small integration helper for strategy/economic gates."""
    return assessment.fresh and assessment.allow_new_entry and assessment.projected_cost_usd is not None

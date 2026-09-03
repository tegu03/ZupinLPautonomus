"""Adaptive range candidate generation for Robinhood Chain LPs."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .farming_intelligence import MarketRegime, RangeCandidate
D=Decimal
@dataclass(frozen=True)
class MarketSnapshot:
    price_usd: Decimal
    volatility_1h_pct: Decimal
    volatility_24h_pct: Decimal
    trend_pct_1h: Decimal
    trend_pct_24h: Decimal
    liquidity_depth_usd: Decimal
    fee_velocity_usd_per_hour: Decimal
    fee_velocity_change_pct: Decimal= D(0)
    def validate(self)->None:
        if self.price_usd<=0 or self.volatility_1h_pct<0 or self.volatility_24h_pct<0 or self.liquidity_depth_usd<0 or self.fee_velocity_usd_per_hour<0:
            raise ValueError("invalid market snapshot")
@dataclass(frozen=True)
class RangeScore:
    candidate: RangeCandidate
    score: Decimal
    regime: MarketRegime
    reason: str

def classify_regime(m: MarketSnapshot)->MarketRegime:
    m.validate()
    if m.volatility_1h_pct >= max(D("5"), m.volatility_24h_pct*D("1.5")): return MarketRegime.HIGH_VOLATILITY
    if m.trend_pct_24h >= max(D("2"),m.volatility_24h_pct*D("0.35")): return MarketRegime.TREND_UP
    if m.trend_pct_24h <= -max(D("2"),m.volatility_24h_pct*D("0.35")): return MarketRegime.TREND_DOWN
    return MarketRegime.RANGE_BOUND

def generate_candidates(m: MarketSnapshot)->list[RangeCandidate]:
    """Generate conservative percent ranges; actual tick conversion belongs to V3/V4 adapters."""
    regime=classify_regime(m)
    vol=max(m.volatility_1h_pct,m.volatility_24h_pct/D(4),D("0.25"))
    widths=[max(D("0.5"),vol*x) for x in (D("0.75"),D("1.25"),D("2"),D("3"))]
    out=[]
    for w in widths:
        if regime==MarketRegime.TREND_UP: lo,hi=-w*D("0.55"),w*D("1.45")
        elif regime==MarketRegime.TREND_DOWN: lo,hi=-w*D("1.45"),w*D("0.55")
        else: lo,hi=-w,w
        out.append(RangeCandidate(lo,hi,D("0"),D("0")))
    return out

def score_range(candidate:RangeCandidate,m:MarketSnapshot,base_capture:D|Decimal)->RangeScore:
    """Score geometry; caller supplies empirical active/capture estimates."""
    regime=classify_regime(m)
    width=candidate.width_pct
    if width<=0: raise ValueError("range upper must exceed lower")
    vol=max(m.volatility_1h_pct,D("0.25"))
    expected_stay=min(D(1),width/(vol*D("2")))
    expected_stay=max(D(0),expected_stay)
    capture=max(D(0),min(D(1),D(base_capture)))
    score=expected_stay*capture
    if regime==MarketRegime.TREND_UP and candidate.upper_pct<=0: score*=D("0.5")
    if regime==MarketRegime.TREND_DOWN and candidate.lower_pct>=0: score*=D("0.5")
    return RangeScore(RangeCandidate(candidate.lower_pct,candidate.upper_pct,expected_stay,capture,candidate.expected_il_usd,candidate.expected_slippage_usd),score,regime,"higher expected in-range occupancy")

def optimize(m:MarketSnapshot,base_capture:D|Decimal)->RangeScore:
    scored=[score_range(c,m,base_capture) for c in generate_candidates(m)]
    return max(scored,key=lambda x:x.score)

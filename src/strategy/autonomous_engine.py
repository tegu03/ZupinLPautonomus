"""High-level deterministic planner joining market, range and economics layers."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .farming_intelligence import PoolOpportunity,RangeCandidate,decide_entry
from .range_optimizer import MarketSnapshot,optimize
D=Decimal
@dataclass(frozen=True)
class AutonomousPlan:
    action:str
    pool_id:str
    lower_pct:D|Decimal|None
    upper_pct:D|Decimal|None
    expected_fee_usd:Decimal
    expected_net_usd:Decimal
    reason:str

def plan_entry(pool:PoolOpportunity,market:MarketSnapshot,capital_usd:Decimal,horizon_days:Decimal,gas_per_tx_usd:Decimal,lifecycle_tx_count:int,minimum_net_profit_usd:Decimal,base_fee_capture:D|Decimal)->AutonomousPlan:
    if not pool.security_pass: return AutonomousPlan("REJECT",pool.pool_id,None,None,D(0),D("-Infinity"),"pool security gate failed")
    optimized=optimize(market,base_fee_capture)
    candidates=[RangeCandidate(optimized.candidate.lower_pct,optimized.candidate.upper_pct,optimized.candidate.expected_active_fraction,optimized.candidate.expected_fee_capture_fraction,optimized.candidate.expected_il_usd,optimized.candidate.expected_slippage_usd)]
    decision=decide_entry(pool,candidates,capital_usd,horizon_days,gas_per_tx_usd,lifecycle_tx_count,minimum_net_profit_usd)
    return AutonomousPlan(decision.action,pool.pool_id,decision.range_lower_pct,decision.range_upper_pct,decision.expected_fee_usd,decision.expected_net_usd,decision.reason)

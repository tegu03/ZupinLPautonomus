"""Fail-closed economic gates for autonomous LP lifecycle actions."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
D=Decimal
@dataclass(frozen=True)
class LifecycleCost:
    gas_usd: Decimal
    mandatory_fees_usd: Decimal= D(0)
    execution_slippage_usd: Decimal= D(0)
    verified_refund_usd: Decimal= D(0)
    def total(self)->Decimal:
        if min(self.gas_usd,self.mandatory_fees_usd,self.execution_slippage_usd,self.verified_refund_usd)<0: raise ValueError("costs must be non-negative")
        return self.gas_usd+self.mandatory_fees_usd+self.execution_slippage_usd-self.verified_refund_usd
@dataclass(frozen=True)
class EconomicConfig:
    max_execution_cost_usd: Decimal=D("1.2")
    minimum_net_benefit_usd: Decimal=D("0.5")
    risk_buffer_usd: Decimal=D("0")
    require_fresh_gas: bool=True
    fail_closed_unknown_cost: bool=True
@dataclass(frozen=True)
class EconomicResult:
    expected_fee_usd: Decimal
    expected_il_usd: Decimal
    lifecycle_cost_usd: Decimal
    risk_buffer_usd: Decimal
    expected_net_usd: Decimal
    passes: bool
    reason: str

def evaluate(expected_fee_usd:D|Decimal,expected_il_usd:D|Decimal,cost:LifecycleCost,config:EconomicConfig,gas_fresh:bool=True)->EconomicResult:
    fee=D(expected_fee_usd); il=D(expected_il_usd); total=cost.total()
    if fee<0 or il<0: raise ValueError("expected fee and IL must be non-negative")
    if config.max_execution_cost_usd<0 or config.minimum_net_benefit_usd<0 or config.risk_buffer_usd<0: raise ValueError("invalid economic config")
    if config.require_fresh_gas and not gas_fresh:
        return EconomicResult(fee,il,total,config.risk_buffer_usd,fee-il-total-config.risk_buffer_usd,False,"stale gas estimate")
    if config.fail_closed_unknown_cost and total is None:
        return EconomicResult(fee,il,D(0),config.risk_buffer_usd,D("-Infinity"),False,"unknown execution cost")
    net=fee-il-total-config.risk_buffer_usd
    passes=total<=config.max_execution_cost_usd and net>config.minimum_net_benefit_usd
    reason="economic gate passed" if passes else "economic gate failed"
    return EconomicResult(fee,il,total,config.risk_buffer_usd,net,passes,reason)

from decimal import Decimal as D
from pytest import raises
from src.execution.gateway import ExecutionDisabled,ExecutionGateway,ExecutionPolicy
from src.strategy.lifecycle import PositionLifecycle,PositionState
from src.strategy.range_optimizer import MarketSnapshot,classify_regime,generate_candidates,optimize
from src.strategy.economics import EconomicConfig,LifecycleCost,evaluate
from src.strategy.farming_intelligence import MarketRegime

def market():
    return MarketSnapshot(D("1"),D("1"),D("2"),D("0.2"),D("0.3"),D("100000"),D("50"))

def test_range_optimizer_generates_adaptive_candidates():
    m=market(); assert classify_regime(m)==MarketRegime.RANGE_BOUND; assert len(generate_candidates(m))==4; assert optimize(m,D("0.5").__class__("0.5")).candidate.lower_pct < 0

def test_trend_up_is_asymmetric():
    m=MarketSnapshot(D("1"),D("1"),D("3"),D("1"),D("4"),D("100000"),D("50"))
    c=generate_candidates(m)[0]; assert c.upper_pct > abs(c.lower_pct)

def test_economic_gate_fails_stale_gas():
    r=evaluate(D("10"),D("1"),LifecycleCost(D("1")),EconomicConfig(),gas_fresh=False); assert not r.passes

def test_economic_gate_includes_all_costs():
    r=evaluate(D("10"),D("1"),LifecycleCost(D("1"),D("0.2"),D("0.3")),EconomicConfig()); assert r.expected_net_usd==D("7.5")

def test_lifecycle_is_fail_closed():
    p=PositionLifecycle("x"); p.transition(PositionState.SIMULATED); p.transition(PositionState.ENTERING); p.transition(PositionState.ACTIVE); p.transition(PositionState.REBALANCING); p.transition(PositionState.ACTIVE); assert p.state==PositionState.ACTIVE
    with raises(ValueError): p.transition(PositionState.CLOSED)

def test_execution_is_disabled_by_default():
    with raises(ExecutionDisabled): ExecutionGateway(ExecutionPolicy()).submit(4663,{})

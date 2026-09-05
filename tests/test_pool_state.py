from zupin.chain.pool_discovery import PoolKey, PoolObservation
from zupin.chain.pool_state import PoolStateObservation, verify_pool_state


POOL_ID = "0x" + "11" * 32


def _pool() -> PoolObservation:
    return PoolObservation(
        pool_key=PoolKey(
            token0="0x0000000000000000000000000000000000000001",
            token1="0x0000000000000000000000000000000000000002",
            fee=500,
            tick_spacing=10,
            hook="0x0000000000000000000000000000000000000000",
        ),
        observed_at=__import__("datetime").datetime(2026, 1, 1),
        source_ref="fixture://pool",
        pool_id=POOL_ID,
    )


def _state(**overrides) -> PoolStateObservation:
    values = dict(
        pool_id=POOL_ID,
        sqrt_price_x96=1 << 96,
        tick=0,
        protocol_fee=0,
        lp_fee=500,
        active_liquidity=1_000_000,
        observed_block=100,
        source_ref="fixture://state",
    )
    values.update(overrides)
    return PoolStateObservation(**values)


def test_consistent_state_is_proven():
    assert verify_pool_state(_pool(), _state()).status == "PROVEN"


def test_mismatched_pool_id_is_conflicted():
    result = verify_pool_state(_pool(), _state(pool_id="0x" + "22" * 32))
    assert result.status == "CONFLICTED"


def test_mismatched_lp_fee_is_conflicted():
    result = verify_pool_state(_pool(), _state(lp_fee=3000))
    assert result.status == "CONFLICTED"


def test_uninitialized_pool_is_unknown():
    result = verify_pool_state(_pool(), _state(sqrt_price_x96=0))
    assert result.status == "UNKNOWN"


def test_non_proven_state_is_not_executable():
    result = verify_pool_state(_pool(), _state(evidence_status="INFERRED"))
    assert result.status == "UNKNOWN"

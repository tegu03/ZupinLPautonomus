from zupin.chain.controlled_harness import (
    MINT_POSITION,
    SETTLE_PAIR,
    SWEEP,
    build_controlled_native_mint_vector,
)
from zupin.chain.pool_discovery import PoolKey


POOL_KEY = PoolKey(
    token0="0x0000000000000000000000000000000000000000",
    token1="0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168",
    fee=500,
    tick_spacing=10,
    hook="0x0000000000000000000000000000000000000000",
)
RECIPIENT = "0x0000000000000000000000000000000000000009"


def test_controlled_native_mint_vector_has_documented_actions():
    vector = build_controlled_native_mint_vector(
        pool_key=POOL_KEY,
        recipient=RECIPIENT,
        tick_lower=-100,
        tick_upper=100,
        liquidity=10**12,
        amount0_max=10**15,
        amount1_max=10**6,
        deadline=1_800_000_000,
    )
    assert vector.pool_id == "0x387bf619da4d3fb62bb276482693dba1b9b3520f573cabdfe033384a24125982"
    assert vector.actions == bytes((MINT_POSITION, SETTLE_PAIR, SWEEP))
    assert vector.calldata.startswith("0xdd46508f")
    assert vector.value_wei == 10**15


def test_controlled_native_mint_vector_is_deterministic():
    kwargs = dict(
        pool_key=POOL_KEY,
        recipient=RECIPIENT,
        tick_lower=-100,
        tick_upper=100,
        liquidity=10**12,
        amount0_max=10**15,
        amount1_max=10**6,
        deadline=1_800_000_000,
    )
    first = build_controlled_native_mint_vector(**kwargs)
    second = build_controlled_native_mint_vector(**kwargs)
    assert first.calldata == second.calldata
    assert first.params == second.params


def test_controlled_native_mint_requires_native_token0():
    non_native = PoolKey(
        token0="0x0000000000000000000000000000000000000001",
        token1=POOL_KEY.token1,
        fee=POOL_KEY.fee,
        tick_spacing=POOL_KEY.tick_spacing,
        hook=POOL_KEY.hook,
    )
    try:
        build_controlled_native_mint_vector(
            pool_key=non_native,
            recipient=RECIPIENT,
            tick_lower=-100,
            tick_upper=100,
            liquidity=1,
            amount0_max=1,
            amount1_max=1,
            deadline=1,
        )
    except ValueError as exc:
        assert "native currency" in str(exc)
    else:
        raise AssertionError("non-native token0 must be rejected")

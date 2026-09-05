from eth_abi import encode
import pytest

from zupin.chain.controlled_harness import (
    MINT_POSITION,
    SETTLE_PAIR,
    SWEEP,
    _abi_encode_bytes_and_bytes_array,
    _abi_encode_modify_liquidities,
    _mint_params,
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


def _reference_mint_params() -> bytes:
    return encode(
        [
            "(address,address,uint24,int24,address)",
            "int24",
            "int24",
            "uint256",
            "uint128",
            "uint128",
            "address",
            "bytes",
        ],
        [
            (
                POOL_KEY.token0,
                POOL_KEY.token1,
                POOL_KEY.fee,
                POOL_KEY.tick_spacing,
                POOL_KEY.hook,
            ),
            -100,
            100,
            10**12,
            10**15,
            10**6,
            RECIPIENT,
            b"",
        ],
    )


def test_controlled_mint_matches_independent_abi_reference():
    actual_mint = _mint_params(
        POOL_KEY,
        -100,
        100,
        10**12,
        10**15,
        10**6,
        RECIPIENT,
        b"",
    )
    assert actual_mint == _reference_mint_params()

    actions = bytes((MINT_POSITION, SETTLE_PAIR, SWEEP))
    reference_settle = encode(["address", "address"], [POOL_KEY.token0, POOL_KEY.token1])
    reference_sweep = encode(["address", "address"], [POOL_KEY.token0, RECIPIENT])
    reference_unlock = encode(
        ["bytes", "bytes[]"],
        [actions, [actual_mint, reference_settle, reference_sweep]],
    )
    assert _abi_encode_bytes_and_bytes_array(
        actions, [actual_mint, reference_settle, reference_sweep]
    ) == reference_unlock

    assert _abi_encode_modify_liquidities(reference_unlock, 1_800_000_000) == (
        "0xdd46508f"
        + encode(["bytes", "uint256"], [reference_unlock, 1_800_000_000]).hex()
    )


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


@pytest.mark.parametrize("field_index", [4, 5])
def test_controlled_mint_rejects_uint128_overflow(field_index):
    values = [POOL_KEY, -100, 100, 1, 1, 1, RECIPIENT, b""]
    values[field_index] = 1 << 128
    with pytest.raises(ValueError, match="uint128"):
        _mint_params(*values)


@pytest.mark.parametrize("field_index", [4, 5])
def test_controlled_mint_rejects_uint128_negative(field_index):
    values = [POOL_KEY, -100, 100, 1, 1, 1, RECIPIENT, b""]
    values[field_index] = -1
    with pytest.raises(ValueError, match="uint128"):
        _mint_params(*values)


def test_controlled_native_mint_requires_native_token0():
    non_native = PoolKey(
        token0="0x0000000000000000000000000000000000000001",
        token1=POOL_KEY.token1,
        fee=POOL_KEY.fee,
        tick_spacing=POOL_KEY.tick_spacing,
        hook=POOL_KEY.hook,
    )
    with pytest.raises(ValueError, match="native currency"):
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

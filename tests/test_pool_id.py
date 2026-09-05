from zupin.chain.pool_discovery import PoolKey
from zupin.chain.pool_id import derive_pool_id


def test_native_usdg_candidate_pool_id_matches_secondary_reference() -> None:
    pool = PoolKey(
        token0="0x0000000000000000000000000000000000000000",
        token1="0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168",
        fee=500,
        tick_spacing=10,
        hook="0x0000000000000000000000000000000000000000",
    )
    assert derive_pool_id(pool) == (
        "0x387bf619da4d3fb62bb276482693dba1b9b3520f573cabdfe033384a24125982"
    )


def test_pool_id_changes_when_pool_key_changes() -> None:
    base = PoolKey(
        token0="0x0000000000000000000000000000000000000000",
        token1="0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168",
        fee=500,
        tick_spacing=10,
        hook="0x0000000000000000000000000000000000000000",
    )
    changed = PoolKey(
        token0=base.token0,
        token1=base.token1,
        fee=3000,
        tick_spacing=10,
        hook=base.hook,
    )
    assert derive_pool_id(base) != derive_pool_id(changed)

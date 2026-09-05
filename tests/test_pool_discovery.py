from datetime import datetime, timezone

from zupin.chain.pool_discovery import (
    PoolKey,
    PoolObservation,
    discover_pool,
    validate_pool_key,
)


def _key(token0="0x0000000000000000000000000000000000000001", token1="0x0000000000000000000000000000000000000002"):
    return PoolKey(token0=token0, token1=token1, fee=500, tick_spacing=10, hook="0x0000000000000000000000000000000000000000")


def _obs(key, status="PROVEN", source="fixture://pool-a", second=0):
    return PoolObservation(key, datetime(2026, 1, 1, 0, 0, second, tzinfo=timezone.utc), source, status)


def test_valid_pool_key_requires_sorted_tokens():
    validate_pool_key(_key())


def test_unsorted_tokens_fail_closed():
    result = discover_pool([_obs(_key(token0="0x0000000000000000000000000000000000000002", token1="0x0000000000000000000000000000000000000001"))])
    assert result.status == "UNKNOWN"
    assert result.pool is None


def test_missing_observation_is_unknown():
    result = discover_pool([])
    assert result.status == "UNKNOWN"


def test_latest_non_proven_evidence_is_not_executable():
    result = discover_pool([_obs(_key(), status="INFERRED", second=1), _obs(_key(), second=0)])
    assert result.status == "UNKNOWN"
    assert result.pool is None


def test_latest_proven_conflict_is_conflicted():
    key_a = _key()
    key_b = _key(token1="0x0000000000000000000000000000000000000003")
    result = discover_pool([_obs(key_a, source="fixture://a", second=1), _obs(key_b, source="fixture://b", second=1)])
    assert result.status == "CONFLICTED"
    assert result.pool is None


def test_consistent_latest_proven_observation_is_proven():
    key = _key()
    result = discover_pool([_obs(key, source="fixture://older"), _obs(key, source="fixture://newer", second=1)])
    assert result.status == "PROVEN"
    assert result.pool is not None
    assert result.pool.source_ref == "fixture://newer"

from src.protocols.v4.position_info import decode_position_info


def pack(pool_prefix: int, lower: int, upper: int, subscriber: int = 0) -> int:
    return (pool_prefix << 56) | ((upper & 0xFFFFFF) << 32) | ((lower & 0xFFFFFF) << 8) | subscriber


def test_position_info_decodes_positive_ticks() -> None:
    pool = int("0123456789abcdef0123456789abcdef0123456789abcdef01", 16)
    info = decode_position_info(pack(pool, -100, 200))
    assert info.tick_lower == -100
    assert info.tick_upper == 200
    assert not info.has_subscriber
    assert info.pool_id_truncated.hex() == "0123456789abcdef0123456789abcdef0123456789abcdef01"


def test_position_info_decodes_negative_24bit_ticks_and_flag() -> None:
    pool = int("abcdef0123456789abcdef0123456789abcdef0123456789ab", 16)
    info = decode_position_info(pack(pool, -887272, 887272, 1))
    assert info.tick_lower == -887272
    assert info.tick_upper == 887272
    assert info.has_subscriber


def test_position_info_rejects_out_of_range_raw_values() -> None:
    try:
        decode_position_info(1 << 256)
    except ValueError:
        pass
    else:
        raise AssertionError("expected uint256 range validation")

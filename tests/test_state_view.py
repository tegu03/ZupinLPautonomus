import pytest

from zupin.chain.state_view import (
    GET_LIQUIDITY_SELECTOR,
    GET_SLOT0_SELECTOR,
    StateViewReadError,
    _decode_signed_int24,
    _decode_words,
    _pool_id_word,
)


def test_selectors_are_verified_stateview_selectors():
    assert GET_SLOT0_SELECTOR == "0xc815641c"
    assert GET_LIQUIDITY_SELECTOR == "0xfa6793d5"


def test_pool_id_is_encoded_as_one_abi_word():
    pool_id = "0x" + "11" * 32
    assert _pool_id_word(pool_id) == "11" * 32


def test_pool_id_rejects_wrong_length():
    with pytest.raises(StateViewReadError):
        _pool_id_word("0x1234")


def test_signed_int24_decoding():
    assert _decode_signed_int24(0) == 0
    assert _decode_signed_int24(10) == 10
    assert _decode_signed_int24((1 << 24) - 1) == -1
    assert _decode_signed_int24((1 << 23) + 5) == -(1 << 23) + 5


def test_decode_words_requires_exact_abi_size():
    assert _decode_words("0x" + "00" * 64, 2) == [0, 0]
    with pytest.raises(StateViewReadError):
        _decode_words("0x" + "00" * 31, 1)


def test_reader_module_contains_no_broadcast_method():
    import zupin.chain.state_view as state_view

    assert not hasattr(state_view, "send_raw_transaction")
    assert not hasattr(state_view, "sign_transaction")

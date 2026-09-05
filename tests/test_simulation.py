from zupin.chain.simulation import simulate_position_manager_call
from zupin.chain.robinhood import UNISWAP_V4_POSITION_MANAGER


def test_simulation_fails_closed_for_wrong_chain() -> None:
    result = simulate_position_manager_call(
        rpc_url="http://unused",
        chain_id=46630,
        from_address="0x0000000000000000000000000000000000000001",
        calldata="0xdd46508f",
    )
    assert result.status == "CONFLICTED"
    assert not result.eth_call_ok


def test_simulation_fails_closed_for_wrong_target() -> None:
    result = simulate_position_manager_call(
        rpc_url="http://unused",
        chain_id=4663,
        from_address="0x0000000000000000000000000000000000000001",
        calldata="0xdd46508f",
        target="0x0000000000000000000000000000000000000002",
    )
    assert result.status == "UNKNOWN"
    assert not result.eth_call_ok


def test_simulation_fails_closed_for_wrong_selector() -> None:
    result = simulate_position_manager_call(
        rpc_url="http://unused",
        chain_id=4663,
        from_address="0x0000000000000000000000000000000000000001",
        calldata="0x12345678",
        target=UNISWAP_V4_POSITION_MANAGER,
    )
    assert result.status == "UNKNOWN"
    assert not result.eth_call_ok


def test_simulation_rejects_malformed_calldata() -> None:
    result = simulate_position_manager_call(
        rpc_url="http://unused",
        chain_id=4663,
        from_address="0x0000000000000000000000000000000000000001",
        calldata="not-calldata",
        target=UNISWAP_V4_POSITION_MANAGER,
    )
    assert result.status == "UNKNOWN"
    assert not result.eth_call_ok


def test_simulation_never_exposes_broadcast_method() -> None:
    assert not hasattr(simulate_position_manager_call, "send_raw_transaction")

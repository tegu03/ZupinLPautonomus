import pytest

from zupin.chain import simulation
from zupin.chain.robinhood import UNISWAP_V4_POSITION_MANAGER


FROM = "0x0000000000000000000000000000000000000001"
CALLDATA = "0xdd46508f00"


def test_simulation_fails_closed_on_rpc_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args, **kwargs):
        raise simulation.SimulationError("RPC transport failure: unavailable")

    monkeypatch.setattr(simulation, "_rpc", fail)
    result = simulation.simulate_position_manager_call(
        rpc_url="http://controlled.invalid",
        chain_id=4663,
        from_address=FROM,
        calldata=CALLDATA,
        target=UNISWAP_V4_POSITION_MANAGER,
    )
    assert result.status == "UNKNOWN"
    assert not result.eth_call_ok
    assert result.gas_estimate is None
    assert "transport failure" in result.reason


def test_simulation_requires_eth_estimate_gas_hex(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = iter(["0x", 123])

    def fake_rpc(*args, **kwargs):
        return next(calls)

    monkeypatch.setattr(simulation, "_rpc", fake_rpc)
    result = simulation.simulate_position_manager_call(
        rpc_url="http://controlled.invalid",
        chain_id=4663,
        from_address=FROM,
        calldata=CALLDATA,
        target=UNISWAP_V4_POSITION_MANAGER,
    )
    assert result.status == "UNKNOWN"
    assert not result.eth_call_ok
    assert result.gas_estimate is None
    assert "non-hex" in result.reason


def test_simulation_proves_controlled_rpc_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_rpc(rpc_url, method, params, timeout=15.0):
        calls.append((method, params))
        if method == "eth_call":
            return "0x"
        if method == "eth_estimateGas":
            return "0x5208"
        raise AssertionError(method)

    monkeypatch.setattr(simulation, "_rpc", fake_rpc)
    result = simulation.simulate_position_manager_call(
        rpc_url="http://controlled.invalid",
        chain_id=4663,
        from_address=FROM,
        calldata=CALLDATA,
        value_wei=17,
        target=UNISWAP_V4_POSITION_MANAGER,
    )

    assert result.status == "PROVEN"
    assert result.eth_call_ok
    assert result.gas_estimate == 21000
    assert len(calls) == 2
    assert calls[0][0] == "eth_call"
    assert calls[1][0] == "eth_estimateGas"
    tx = calls[0][1][0]
    assert tx["from"] == FROM
    assert tx["to"] == UNISWAP_V4_POSITION_MANAGER
    assert tx["data"] == CALLDATA
    assert tx["value"] == hex(17)
    assert calls[0][1][1] == "latest"
    assert calls[1][1][1] == "latest"

from zupin.chain.robinhood import (
    ROBINHOOD_CHAIN_ID,
    UNISWAP_V4_CONTRACTS,
    probe_read_only,
)


def make_rpc(chain_id="0x1237", code="0x6000"):
    def rpc(method, params=None):
        if method == "eth_chainId":
            return chain_id
        if method == "eth_getCode":
            return code
        raise AssertionError(method)

    return rpc


def test_probe_requires_robinhood_chain_id_and_all_core_contracts():
    result = probe_read_only(make_rpc(chain_id=hex(ROBINHOOD_CHAIN_ID)))

    assert result.status == "PROVEN"
    assert result.rpc_chain_id == ROBINHOOD_CHAIN_ID
    assert set(result.contracts_have_code) == set(UNISWAP_V4_CONTRACTS)
    assert all(result.contracts_have_code.values())


def test_probe_marks_chain_id_mismatch_conflicted():
    result = probe_read_only(make_rpc(chain_id="0x1"))

    assert result.status == "CONFLICTED"
    assert result.rpc_chain_id == 1


def test_probe_marks_missing_runtime_code_unknown():
    result = probe_read_only(make_rpc(chain_id=hex(ROBINHOOD_CHAIN_ID), code="0x"))

    assert result.status == "UNKNOWN"
    assert not any(result.contracts_have_code.values())


def test_probe_rejects_malformed_chain_id():
    def rpc(method, params=None):
        assert method == "eth_chainId"
        return 4663

    try:
        probe_read_only(rpc)
    except RuntimeError as exc:
        assert "eth_chainId" in str(exc)
    else:
        raise AssertionError("malformed chain ID must fail closed")


def test_probe_does_not_convert_transport_failure_to_proven():
    def rpc(method, params=None):
        raise OSError("network unavailable")

    try:
        probe_read_only(rpc)
    except OSError:
        pass
    else:
        raise AssertionError("transport failure must propagate for UNKNOWN evidence")

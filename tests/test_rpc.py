from __future__ import annotations

import httpx
import pytest

from src.infrastructure.chain import ROBINHOOD_CHAIN_ID, WrongChainError
from src.infrastructure.rpc import RobinhoodRpcClient, RpcConfig, RpcResponseError


def make_client(handler) -> RobinhoodRpcClient:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    return RobinhoodRpcClient(RpcConfig("http://test", max_attempts=1), client=client)


def test_chain_id_decodes_hex() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": hex(ROBINHOOD_CHAIN_ID)})

    rpc = make_client(handler)
    try:
        assert rpc.chain_id() == 4663
        rpc.assert_chain()
    finally:
        rpc.close()


def test_wrong_chain_fails_closed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": "0x1"})

    rpc = make_client(handler)
    try:
        with pytest.raises(WrongChainError):
            rpc.assert_chain()
    finally:
        rpc.close()


def test_rpc_error_is_not_silently_accepted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"jsonrpc": "2.0", "id": 1, "error": {"code": -32000, "message": "boom"}},
        )

    rpc = make_client(handler)
    try:
        with pytest.raises(RpcResponseError):
            rpc.call("eth_blockNumber")
    finally:
        rpc.close()


def test_block_number_decodes_hex() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": "0x1234"})

    rpc = make_client(handler)
    try:
        assert rpc.block_number() == 0x1234
    finally:
        rpc.close()

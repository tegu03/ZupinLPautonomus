"""Deterministic JSON-RPC client for Robinhood Chain.

This module is deliberately small: protocol-specific logic belongs in protocol
adapters, not in the transport layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .chain import ROBINHOOD_CHAIN_ID, WrongChainError


class RpcError(RuntimeError):
    """Base class for JSON-RPC failures."""


class RpcTransportError(RpcError):
    """Network/HTTP transport failure."""


class RpcResponseError(RpcError):
    """JSON-RPC returned an error object."""


@dataclass(frozen=True)
class RpcConfig:
    url: str
    timeout_seconds: float = 10.0
    max_attempts: int = 3


class RobinhoodRpcClient:
    """Read-only JSON-RPC client with a mandatory chain-id guard."""

    def __init__(self, config: RpcConfig, client: httpx.Client | None = None) -> None:
        if config.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self._config = config
        self._client = client or httpx.Client(timeout=config.timeout_seconds)
        self._owns_client = client is None
        self._request_id = 0
        self._call_with_retry: Callable[[str, list[Any] | None], Any] = self._build_retry_call()

    def _build_retry_call(self) -> Callable[[str, list[Any] | None], Any]:
        @retry(
            stop=stop_after_attempt(self._config.max_attempts),
            wait=wait_exponential(multiplier=0.2, min=0.2, max=2.0),
            retry=retry_if_exception_type(RpcTransportError),
            reraise=True,
        )
        def execute(method: str, params: list[Any] | None = None) -> Any:
            self._request_id += 1
            payload = {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params or []}
            try:
                response = self._client.post(self._config.url, json=payload)
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise RpcTransportError(f"RPC transport failure for {method}: {exc}") from exc
            if not isinstance(data, dict):
                raise RpcResponseError(f"Malformed JSON-RPC response for {method}")
            if data.get("error") is not None:
                raise RpcResponseError(f"RPC error for {method}: {data['error']}")
            if "result" not in data:
                raise RpcResponseError(f"Missing result for {method}")
            return data["result"]

        return execute

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "RobinhoodRpcClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        """Execute one JSON-RPC request and return only the result."""
        return self._call_with_retry(method, params)

    def chain_id(self) -> int:
        value = self.call("eth_chainId")
        if not isinstance(value, str):
            raise RpcResponseError("eth_chainId returned a non-hex value")
        try:
            return int(value, 16)
        except ValueError as exc:
            raise RpcResponseError(f"Invalid eth_chainId value: {value}") from exc

    def assert_chain(self) -> None:
        actual = self.chain_id()
        if actual != ROBINHOOD_CHAIN_ID:
            raise WrongChainError(f"Wrong chain: expected {ROBINHOOD_CHAIN_ID}, got {actual}")

    def block_number(self) -> int:
        value = self.call("eth_blockNumber")
        if not isinstance(value, str):
            raise RpcResponseError("eth_blockNumber returned a non-hex value")
        try:
            return int(value, 16)
        except ValueError as exc:
            raise RpcResponseError(f"Invalid block number: {value}") from exc

    def get_block(self, block: str = "latest", full_transactions: bool = False) -> dict[str, Any]:
        value = self.call("eth_getBlockByNumber", [block, full_transactions])
        if not isinstance(value, dict):
            raise RpcResponseError(f"eth_getBlockByNumber returned {type(value).__name__}")
        return value

    def get_code(self, address: str, block: str = "latest") -> str:
        value = self.call("eth_getCode", [address, block])
        if not isinstance(value, str):
            raise RpcResponseError("eth_getCode returned a non-string value")
        return value

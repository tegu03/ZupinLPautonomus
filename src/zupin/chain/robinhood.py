"""Read-only Robinhood Chain capability verification.

This module intentionally performs no transaction signing or broadcasting.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen
import json

ROBINHOOD_CHAIN_ID = 4663
ROBINHOOD_RPC_URL = "https://rpc.mainnet.chain.robinhood.com"
UNISWAP_V4_POOL_MANAGER = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
UNISWAP_V4_POSITION_MANAGER = "0x58daec3116aae6d93017baaea7749052e8a04fa7"
UNISWAP_V4_QUOTER = "0x8dc178efb8111bb0973dd9d722ebeff267c98f94"


@dataclass(frozen=True)
class CapabilityProbe:
    chain_id: int
    rpc_chain_id: int | None
    contracts_have_code: dict[str, bool]
    status: str
    reason: str


def _rpc(method: str, params: list[Any] | None = None, timeout: float = 10.0) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}).encode()
    request = Request(ROBINHOOD_RPC_URL, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode())
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    return result["result"]


def probe_read_only() -> CapabilityProbe:
    rpc_chain_id = int(_rpc("eth_chainId"), 16)
    addresses = {
        "pool_manager": UNISWAP_V4_POOL_MANAGER,
        "position_manager": UNISWAP_V4_POSITION_MANAGER,
        "quoter": UNISWAP_V4_QUOTER,
    }
    code = {name: _rpc("eth_getCode", [address, "latest"]) != "0x" for name, address in addresses.items()}
    if rpc_chain_id != ROBINHOOD_CHAIN_ID:
        return CapabilityProbe(ROBINHOOD_CHAIN_ID, rpc_chain_id, code, "CONFLICTED", "RPC chain ID mismatch")
    if not all(code.values()):
        return CapabilityProbe(ROBINHOOD_CHAIN_ID, rpc_chain_id, code, "UNKNOWN", "One or more required contracts have no runtime bytecode")
    return CapabilityProbe(ROBINHOOD_CHAIN_ID, rpc_chain_id, code, "PROVEN", "Robinhood RPC and required Uniswap v4 contracts are live")

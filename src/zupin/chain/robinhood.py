"""Read-only Robinhood Chain capability verification.

This module intentionally performs no transaction signing or broadcasting.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from urllib.request import Request, urlopen
import json

ROBINHOOD_CHAIN_ID = 4663
ROBINHOOD_RPC_URL = "https://rpc.mainnet.chain.robinhood.com"

# Canonical Uniswap deployments published for Robinhood Chain (4663).
# These constants are configuration/evidence inputs only; they do not authorize writes.
UNISWAP_V4_CONTRACTS = {
    "pool_manager": "0x8366a39cc670b4001a1121b8f6a443a643e40951",
    "position_manager": "0x58daec3116aae6d93017baaea7749052e8a04fa7",
    "v4_quoter": "0x8dc178efb8111bb0973dd9d722ebeff267c98f94",
    "state_view": "0xf3334192d15450cdd385c8b70e03f9a6bd9e673b",
    "swap_router02": "0xcaf681a66d020601342297493863e78c959e5cb2",
    "permit2": "0x000000000022d473030f116ddee9f6b43ac78ba3",
}

# Backward-compatible named constants for existing simulation/test consumers.
# The mapping above remains the single canonical address source.
UNISWAP_V4_POOL_MANAGER = UNISWAP_V4_CONTRACTS["pool_manager"]
UNISWAP_V4_POSITION_MANAGER = UNISWAP_V4_CONTRACTS["position_manager"]
UNISWAP_V4_QUOTER = UNISWAP_V4_CONTRACTS["v4_quoter"]


@dataclass(frozen=True)
class CapabilityProbe:
    chain_id: int
    rpc_chain_id: int | None
    contracts_have_code: dict[str, bool]
    status: str
    reason: str


def _rpc(method: str, params: list[Any] | None = None, timeout: float = 10.0) -> Any:
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
    ).encode()
    request = Request(
        ROBINHOOD_RPC_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode())
    if not isinstance(result, dict) or "result" not in result:
        raise RuntimeError("malformed JSON-RPC response")
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    return result["result"]


def probe_read_only(rpc: Callable[[str, list[Any] | None], Any] = _rpc) -> CapabilityProbe:
    """Probe chain identity and required contract bytecode without any write operation.

    Transport or malformed-response failures are deliberately surfaced to the caller rather
    than converted into PROVEN evidence. Callers must record such a result as UNKNOWN.
    """
    raw_chain_id = rpc("eth_chainId")
    if not isinstance(raw_chain_id, str) or not raw_chain_id.startswith("0x"):
        raise RuntimeError("invalid eth_chainId response")
    rpc_chain_id = int(raw_chain_id, 16)

    code: dict[str, bool] = {}
    for name, address in UNISWAP_V4_CONTRACTS.items():
        runtime_code = rpc("eth_getCode", [address, "latest"])
        if not isinstance(runtime_code, str) or not runtime_code.startswith("0x"):
            raise RuntimeError(f"invalid eth_getCode response for {name}")
        code[name] = runtime_code != "0x"

    if rpc_chain_id != ROBINHOOD_CHAIN_ID:
        return CapabilityProbe(
            ROBINHOOD_CHAIN_ID,
            rpc_chain_id,
            code,
            "CONFLICTED",
            "RPC chain ID mismatch",
        )
    if not all(code.values()):
        return CapabilityProbe(
            ROBINHOOD_CHAIN_ID,
            rpc_chain_id,
            code,
            "UNKNOWN",
            "One or more required Uniswap v4 contracts have no runtime bytecode",
        )
    return CapabilityProbe(
        ROBINHOOD_CHAIN_ID,
        rpc_chain_id,
        code,
        "PROVEN",
        "Robinhood RPC and required Uniswap v4 contracts have runtime bytecode",
    )

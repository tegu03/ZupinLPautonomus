"""Fail-closed, read-only EVM simulation for LP write capabilities.

This module never signs or broadcasts a transaction. It only asks an RPC node
whether a fully encoded call can be executed and what gas the node estimates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen
import json

from .robinhood import ROBINHOOD_CHAIN_ID, UNISWAP_V4_POSITION_MANAGER

POSITION_MANAGER_MODIFY_LIQUIDITIES_SELECTOR = "0xdd46508f"


@dataclass(frozen=True)
class SimulationResult:
    chain_id: int
    target: str
    calldata: str
    value_wei: int
    eth_call_ok: bool
    gas_estimate: int | None
    status: str
    reason: str


class SimulationError(RuntimeError):
    pass


def _rpc(rpc_url: str, method: str, params: list[Any], timeout: float = 15.0) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode())
    if "error" in result:
        raise SimulationError(str(result["error"]))
    return result.get("result")


def simulate_position_manager_call(
    *,
    rpc_url: str,
    chain_id: int,
    from_address: str,
    calldata: str,
    value_wei: int = 0,
    target: str = UNISWAP_V4_POSITION_MANAGER,
) -> SimulationResult:
    """Simulate an already-encoded PositionManager modifyLiquidities call.

    The caller must supply calldata produced by a verified protocol encoder.
    This function deliberately does not construct protocol-specific calldata.
    """
    if chain_id != ROBINHOOD_CHAIN_ID:
        return SimulationResult(chain_id, target, calldata, value_wei, False, None, "CONFLICTED", "unsupported chain ID")
    if target.lower() != UNISWAP_V4_POSITION_MANAGER.lower():
        return SimulationResult(chain_id, target, calldata, value_wei, False, None, "UNKNOWN", "target is not the verified Robinhood v4 PositionManager")
    if not calldata.startswith("0x") or len(calldata) < 10:
        return SimulationResult(chain_id, target, calldata, value_wei, False, None, "UNKNOWN", "calldata is missing or malformed")
    if calldata[:10].lower() != POSITION_MANAGER_MODIFY_LIQUIDITIES_SELECTOR:
        return SimulationResult(chain_id, target, calldata, value_wei, False, None, "UNKNOWN", "calldata selector is not verified PositionManager.modifyLiquidities(bytes,uint256)")
    if not from_address.startswith("0x") or len(from_address) != 42:
        return SimulationResult(chain_id, target, calldata, value_wei, False, None, "UNKNOWN", "from address is missing or malformed")
    if value_wei < 0:
        return SimulationResult(chain_id, target, calldata, value_wei, False, None, "UNKNOWN", "value must be non-negative")

    tx = {"from": from_address, "to": target, "data": calldata}
    if value_wei:
        tx["value"] = hex(value_wei)

    try:
        _rpc(rpc_url, "eth_call", [tx, "latest"])
        gas_hex = _rpc(rpc_url, "eth_estimateGas", [tx, "latest"])
        gas = int(gas_hex, 16) if isinstance(gas_hex, str) else None
    except (SimulationError, ValueError, TypeError) as exc:
        return SimulationResult(chain_id, target, calldata, value_wei, False, None, "UNKNOWN", f"simulation failed: {exc}")

    return SimulationResult(chain_id, target, calldata, value_wei, True, gas, "PROVEN", "eth_call and eth_estimateGas succeeded")

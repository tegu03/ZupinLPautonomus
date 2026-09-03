"""Typed, single-source contract registry for Robinhood Chain.

Addresses are intentionally explicit and chain-scoped. No address may be
selected dynamically from another network.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

from web3 import Web3

from ..chain import ROBINHOOD_CHAIN_ID


@dataclass(frozen=True)
class ProtocolContracts:
    name: str
    enabled: bool
    priority: int
    addresses: dict[str, str]

    def address(self, name: str) -> str:
        try:
            return self.addresses[name]
        except KeyError as exc:
            raise KeyError(f"Unknown {self.name} contract: {name}") from exc


@dataclass(frozen=True)
class ContractRegistry:
    chain_id: int
    protocols: dict[str, ProtocolContracts]

    def __post_init__(self) -> None:
        if self.chain_id != ROBINHOOD_CHAIN_ID:
            raise ValueError(
                f"Contract registry is Robinhood-only: expected {ROBINHOOD_CHAIN_ID}, "
                f"got {self.chain_id}"
            )
        for protocol in self.protocols.values():
            for name, address in protocol.addresses.items():
                if not Web3.is_address(address):
                    raise ValueError(f"Invalid address for {protocol.name}.{name}: {address}")
                if Web3.to_checksum_address(address) == Web3.to_checksum_address("0x0000000000000000000000000000000000000000"):
                    raise ValueError(f"Zero address is forbidden: {protocol.name}.{name}")

    def protocol(self, name: str) -> ProtocolContracts:
        try:
            return self.protocols[name]
        except KeyError as exc:
            raise KeyError(f"Unknown protocol: {name}") from exc

    def all_addresses(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for protocol in self.protocols.values():
            for name, address in protocol.addresses.items():
                result[f"{protocol.name}.{name}"] = Web3.to_checksum_address(address)
        return result


def load_robinhood_registry(path: str | Path) -> ContractRegistry:
    """Load the canonical registry from config/robinhood.json."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Registry configuration must be a JSON object")

    network = raw.get("network")
    protocols_raw = raw.get("protocols")
    if not isinstance(network, dict) or not isinstance(protocols_raw, dict):
        raise ValueError("Registry configuration requires network and protocols")

    chain_id = network.get("chain_id")
    if not isinstance(chain_id, int):
        raise ValueError("network.chain_id must be an integer")

    protocols: dict[str, ProtocolContracts] = {}
    for protocol_name, value in protocols_raw.items():
        if not isinstance(value, dict):
            raise ValueError(f"Protocol {protocol_name} must be an object")
        addresses = {k: v for k, v in value.items() if k not in {"enabled", "priority"}}
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in addresses.items()):
            raise ValueError(f"All addresses in {protocol_name} must be strings")
        enabled = value.get("enabled", True)
        priority = value.get("priority", 100)
        if not isinstance(enabled, bool) or not isinstance(priority, int):
            raise ValueError(f"Invalid enabled/priority in {protocol_name}")
        protocols[protocol_name] = ProtocolContracts(
            name=protocol_name,
            enabled=enabled,
            priority=priority,
            addresses=addresses,
        )

    return ContractRegistry(chain_id=chain_id, protocols=protocols)

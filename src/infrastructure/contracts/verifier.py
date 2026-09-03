"""Runtime verification of configured Robinhood contract deployments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from web3 import Web3

from ..rpc import RobinhoodRpcClient
from .registry import ContractRegistry


class ContractVerificationError(RuntimeError):
    """Raised when a required contract cannot be verified safely."""


@dataclass(frozen=True)
class ContractCheck:
    key: str
    address: str
    code_present: bool
    passed: bool
    detail: str


class ContractVerifier:
    """Fail-closed verifier for configured protocol deployments.

    Bytecode existence is necessary but deliberately not treated as proof that
    an address implements the expected protocol. Protocol-specific ABI checks
    belong in the V3/V4 reader tests and verification adapters.
    """

    def __init__(self, rpc: RobinhoodRpcClient, registry: ContractRegistry) -> None:
        self._rpc = rpc
        self._registry = registry

    @staticmethod
    def _normalize_code(code: str) -> str:
        return code.lower().removeprefix("0x")

    def verify_address(self, key: str, address: str) -> ContractCheck:
        if not Web3.is_address(address):
            return ContractCheck(key, address, False, False, "invalid EVM address")

        checksum = Web3.to_checksum_address(address)
        try:
            code = self._rpc.get_code(checksum)
        except Exception as exc:
            return ContractCheck(key, checksum, False, False, f"RPC verification failed: {exc}")

        normalized = self._normalize_code(code)
        if not normalized or set(normalized) == {"0"}:
            return ContractCheck(key, checksum, False, False, "no contract bytecode")

        return ContractCheck(key, checksum, True, True, "contract bytecode present")

    def verify_all(self) -> list[ContractCheck]:
        # Chain identity is always checked before any deployment decision.
        self._rpc.assert_chain()
        checks = [self.verify_address(key, address) for key, address in self._registry.all_addresses().items()]
        failed = [check for check in checks if not check.passed]
        if failed:
            details = "; ".join(f"{c.key}: {c.detail}" for c in failed)
            raise ContractVerificationError(f"Contract verification failed: {details}")
        return checks


def require_contracts(
    rpc: RobinhoodRpcClient,
    registry: ContractRegistry,
    *,
    keys: list[str] | None = None,
) -> list[ContractCheck]:
    """Verify selected registry addresses before a dependent operation."""
    rpc.assert_chain()
    verifier = ContractVerifier(rpc, registry)
    if keys is None:
        return verifier.verify_all()

    available = registry.all_addresses()
    checks: list[ContractCheck] = []
    for key in keys:
        if key not in available:
            raise ContractVerificationError(f"Unknown registry key: {key}")
        checks.append(verifier.verify_address(key, available[key]))
    failed = [check for check in checks if not check.passed]
    if failed:
        details = "; ".join(f"{c.key}: {c.detail}" for c in failed)
        raise ContractVerificationError(f"Contract verification failed: {details}")
    return checks

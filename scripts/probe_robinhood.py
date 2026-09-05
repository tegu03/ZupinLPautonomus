"""Run the read-only Robinhood Chain capability probe and emit JSON evidence.

This command never signs or broadcasts a transaction. A transport or malformed RPC
failure is emitted as UNKNOWN so the result can never be mistaken for PROVEN evidence.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json

from zupin.chain.robinhood import (
    ROBINHOOD_CHAIN_ID,
    ROBINHOOD_RPC_URL,
    UNISWAP_V4_CONTRACTS,
    probe_read_only,
    rpc_read_only,
)


def main() -> int:
    observed_at = datetime.now(timezone.utc).isoformat()
    try:
        result = probe_read_only()
        raw_block_number = rpc_read_only("eth_blockNumber")
        if not isinstance(raw_block_number, str) or not raw_block_number.startswith("0x"):
            raise RuntimeError("invalid eth_blockNumber response")
        latest_block_number = int(raw_block_number, 16)
        payload = {
            "capability": "robinhood_chain_core_uniswap_contracts",
            "status": result.status,
            "observed_at_utc": observed_at,
            "expected_chain_id": ROBINHOOD_CHAIN_ID,
            "rpc_chain_id": result.rpc_chain_id,
            "latest_block_number": latest_block_number,
            "rpc_url": ROBINHOOD_RPC_URL,
            "contracts": UNISWAP_V4_CONTRACTS,
            "contracts_have_code": result.contracts_have_code,
            "reason": result.reason,
        }
    except Exception as exc:  # noqa: BLE001 - CLI must fail closed on every probe failure.
        payload = {
            "capability": "robinhood_chain_core_uniswap_contracts",
            "status": "UNKNOWN",
            "observed_at_utc": observed_at,
            "expected_chain_id": ROBINHOOD_CHAIN_ID,
            "rpc_chain_id": None,
            "latest_block_number": None,
            "rpc_url": ROBINHOOD_RPC_URL,
            "contracts": UNISWAP_V4_CONTRACTS,
            "contracts_have_code": {},
            "reason": f"probe failed closed: {type(exc).__name__}: {exc}",
        }

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PROVEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())

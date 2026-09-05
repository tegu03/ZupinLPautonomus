# Integration Evidence Registry

This document is the human-readable companion to the persisted `evidence_records` table. It records only evidence that has actually been verified; UNKNOWN is the default for capabilities not yet established.

## Robinhood Chain — 4663

| Capability | Status | Evidence | Notes |
|---|---|---|---|
| `robinhood_chain_evm_4663` | PROVEN | Official Robinhood Chain documentation | EVM-compatible; mainnet chain ID 4663; ETH gas; official RPC and Blockscout are published. |
| `robinhood_public_rpc_4663` | PROVEN | Official Robinhood Chain documentation | Public RPC exists but is rate-limited and not recommended for production. |
| `uniswap_contracts_deployed_4663` | PROVEN | Official Uniswap contracts deployment registry | Chain 4663 has deployed PoolManager, Position Manager, V4 Quoter, Universal Router, and related contracts. |
| `uniswap_v4_lp_write_4663` | UNKNOWN | No controlled Zupin execution verification yet | Exact pool, calldata, simulation, signer policy, reconciliation, and economic checks are not yet proven as one safe write path. |
| `krystal_lp_write_4663` | UNKNOWN | No current primary-source write-path verification in this repository | Discovery/API support is not sufficient to authorize writes. |

## Evidence rules

1. `PROVEN` means the named capability is directly supported by a recorded primary-source and/or on-chain verification.
2. `INFERRED` is never sufficient for execution authorization.
3. `UNKNOWN` and `CONFLICTED` are execution-blocking states.
4. Deployment of a protocol contract does not prove that Zupin's complete write lifecycle is safe.
5. A capability must be re-verified when its contract set, protocol version, route, or relevant assumptions change.

## Current primary-source references

- Robinhood Chain network/deployment documentation: `https://docs.robinhood.com/chain/deploy-smart-contracts/`
- Robinhood Chain connection details: `https://docs.robinhood.com/chain/connecting/`
- Uniswap official chain-4663 deployment registry: `https://github.com/Uniswap/contracts/blob/main/deployments/4663.md`

## Authorization posture

No `UNKNOWN` or `CONFLICTED` capability may cross the execution policy gate. This registry is evidence storage, not a transaction authorization mechanism by itself; the deterministic policy gate remains responsible for authorization.

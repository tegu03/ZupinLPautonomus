# Integration Evidence Registry

This document is the human-readable companion to the persisted `evidence_records` table. It records only evidence that has actually been verified; UNKNOWN is the default for capabilities not yet established.

## Robinhood Chain — 4663

| Capability | Status | Evidence | Notes |
|---|---|---|---|
| `robinhood_chain_evm_4663` | PROVEN | Official Robinhood Chain documentation | EVM-compatible; mainnet chain ID 4663; ETH gas; official RPC and Blockscout are published. |
| `robinhood_public_rpc_4663` | PROVEN | Official Robinhood Chain documentation | Public RPC exists but is rate-limited and not recommended for production. Runtime accessibility from the GitHub Actions environment is separately tracked below. |
| `uniswap_contracts_deployed_4663` | PROVEN | Official Uniswap contracts deployment registry | Chain 4663 lists PoolManager, Position Manager, V4 Quoter, StateView, SwapRouter02, Permit2, and related contracts. This is deployment evidence, not proof of runtime bytecode from Zupin's RPC probe. |
| `robinhood_core_rpc_probe_4663` | UNKNOWN | Zupin read-only runtime probe, GitHub Actions run 33954141064 | The probe executed successfully but the published public RPC returned HTTP 403, so the result was UNKNOWN and the promotion gate correctly refused PROVEN. No chain ID or runtime bytecode evidence was obtained from that run. |
| `uniswap_v4_lp_write_4663` | UNKNOWN | No controlled Zupin execution verification yet | Exact pool, calldata, simulation, signer policy, reconciliation, and economic checks are not yet proven as one safe write path. |
| `krystal_lp_write_4663` | UNKNOWN | No current primary-source write-path verification in this repository | Discovery/API support is not sufficient to authorize writes. |

## Runtime probe access

The runtime probe accepts `ZUPIN_ROBINHOOD_RPC_URL` so a production-grade provider can be supplied without changing code. The GitHub Actions workflow reads this value from the repository secret `ZUPIN_ROBINHOOD_RPC_URL`; when the secret is absent, the code falls back to the official public RPC. Robinhood's documentation recommends a managed provider for production and lists Alchemy, QuickNode, Blockdaemon, dRPC, and Validation Cloud as supported providers.

The first live GitHub Actions probe against the public endpoint returned `HTTP Error 403: Forbidden` on 2026-09-05. This is an access failure, not proof that the chain or contracts are unavailable.

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

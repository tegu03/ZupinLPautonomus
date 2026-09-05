# Evidence & Source Policy

Status: **PHASE 0 — NON-NEGOTIABLE**

## Evidence labels

Every material integration claim is tagged:

- `PROVEN`
- `INFERRED`
- `UNKNOWN`
- `CONFLICTED`

`UNKNOWN` and `CONFLICTED` are not eligible for autonomous execution.

## Source hierarchy

For protocol/chain implementation decisions, use this order:

1. Official chain/protocol documentation.
2. Official API/SDK/GitHub repository.
3. Verified deployed contracts and on-chain state.
4. Official explorer data.
5. Reputable third-party sources only as a secondary cross-check.

A blog, screenshot, model memory, or third-party repository cannot by itself establish production support.

## Evidence record

Each integration capability should have:

- capability name
- chain ID
- protocol/version
- contract address(es)
- source URL/reference
- evidence type
- observed/retrieved timestamp
- verifier/version
- status label
- notes/conflicts

## Current proven baseline

### Robinhood Chain

**PROVEN:** Official Robinhood Chain documentation identifies Robinhood Chain as an Ethereum L2, chain ID `4663`, with ETH as native gas and documents mainnet connectivity. Exact RPC and explorer configuration must be kept in the chain adapter configuration and verified at runtime.

### Uniswap v4 architecture

**PROVEN:** Official Uniswap documentation states that v4 uses a singleton architecture and hooks and supports liquidity lifecycle operations. This does not by itself prove that a particular Robinhood deployment, pool, router, or transaction path is available to Zupin.

### Telegram deletion

**PROVEN:** Telegram Bot API documents `deleteMessage` with platform-specific deletion limitations. Current Bot API documentation also documents ephemeral messages and `deleteEphemeralMessage`. Zupin must treat deletion as exposure reduction, not a guarantee that a secret cannot be retained by a client/user.

### Solana key handling

**PROVEN:** Official Solana documentation states that a keypair contains a public key and private key and warns against embedding private keys in client code or source control; production signing should use an appropriate key-management boundary.

## Unknowns that must remain blocked

The following require primary-source verification before enabling real-money writes on Robinhood:

- exact supported DEXs and versions
- exact LP pool/position-manager contracts
- transaction construction route
- token allowlist and metadata
- fee collection semantics
- range/rebalance semantics
- protocol-specific approval requirements
- supported simulation path
- reliable indexing/reconciliation coverage
- gas estimation behavior under production conditions

Do not fill these gaps from assumptions.

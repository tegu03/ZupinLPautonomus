# Gas Intelligence Foundation

## Purpose

Gas is a lifecycle execution cost, not LP fee income. The gas layer provides a fresh, transaction-specific cost estimate to the strategy/economic gate and prevents new LP entries when the hard gas ceiling is exceeded.

## Hard policy

- Network: Robinhood Chain mainnet, chain ID 4663.
- Maximum gas cost for one required transaction: **$1.30**.
- If projected gas cost is **> $1.30**, state is `GAS_BLOCKED` and NEW LP entries are rejected.
- At exactly $1.30, the transaction is within the hard cap; the broader economic gate must still pass.
- A stale, future-dated, malformed, or otherwise unverifiable gas observation is `GAS_UNKNOWN` and fails closed for new entries.
- Existing positions are not force-exited solely because gas becomes expensive.

## Rolling intelligence

`GasIntelligence` evaluates a transaction-specific observation plus recent observations.

States:

- `GAS_STABLE`: fresh and below the rolling elevated threshold.
- `GAS_ELEVATED`: fresh and below the hard cap, but history is incomplete or current cost is elevated.
- `GAS_BLOCKED`: fresh cost exceeds the $1.30 hard cap.
- `GAS_UNKNOWN`: missing, stale, future-dated, or invalid input.

The layer does not approve profitability. It only supplies a gas-risk decision to the economic gate.

## Cost model

For an EVM transaction:

`gas_cost_usd = gas_limit * max_fee_per_gas_wei / 1e18 * native_token_usd`

The implementation intentionally uses a transaction-specific gas limit and max fee estimate rather than a hardcoded gas price.

## Required next integration

A read-only RPC/market adapter must provide:

1. fresh fee data;
2. a transaction-specific gas estimate for the exact calldata/action;
3. a verified native-token USD price;
4. timestamped observations.

The adapter must not silently substitute stale values. The resulting `GasAssessment` is then consumed by the economic entry gate.

## Important distinction

`max_gas_cost_per_transaction_usd = 1.30` is a hard gas ceiling. `max_net_execution_cost_usd = 1.20` remains a separate total execution-cost policy and is still authoritative. A transaction must satisfy both policies.

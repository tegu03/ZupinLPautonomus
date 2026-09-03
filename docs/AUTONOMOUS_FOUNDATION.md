# Autonomous LP Foundation

Target: Robinhood Chain only, chain ID 4663. Uniswap V4 is primary and V3 secondary.

## Decision pipeline

1. Read on-chain pool and position state.
2. Attribute fees from position-level fee growth; never equate pool APR with LP income.
3. Measure fee velocity over rolling windows.
4. Classify regime: range-bound, trend-up, trend-down, or high-volatility.
5. Generate asymmetric/symmetric range candidates from observed volatility.
6. Score expected occupancy and empirical fee capture.
7. Apply IL, slippage, gas, mandatory fees and risk buffer.
8. Enter only if the economic gate passes.
9. Manage the position through an explicit lifecycle state machine.
10. Keep execution fail-closed until testnet validation authorizes a separate execution implementation.

## Safety invariants

- Wrong chain is a hard failure.
- Unknown/stale execution cost is a hard failure.
- Live signing and broadcast are disabled by default.
- Pool-wide volume is an opportunity signal only.
- Liquidity changes split fee-accounting lifecycles.
- Rebalance must clear incremental economics; it must not react to noise.
- No profitability guarantee is made.

## Testnet gate

Before any mainnet execution is enabled, the system must demonstrate on Robinhood Chain testnet (when a supported testnet deployment and canonical protocol addresses are available):

- chain identity and contract relationship verification;
- deterministic quote/state reads;
- position creation, monitoring, fee accounting, collection and exit in a controlled wallet;
- transaction receipt/revert handling and restart recovery;
- measured gas costs;
- reconciliation between wallet balances, position state and fee-growth accounting;
- shadow/paper results versus actual controlled testnet transactions.

A passing unit-test suite alone is not sufficient for mainnet activation.

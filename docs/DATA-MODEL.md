# Zupin Data Model

Status: **PHASE 0**

## Core entities

- `users` — Telegram identity, account status, autonomy status, created/updated timestamps.
- `wallets` — one logical user wallet record with EVM and SVM addresses; never stores plaintext secrets.
- `key_references` — opaque references to encrypted/key-management records, never private-key material.
- `chains` — chain ID, namespace, RPC metadata, explorer, native asset, capability status.
- `protocols` — DEX/protocol identity, version, contract set, evidence status, enabled status.
- `tokens` — chain-specific token identity, decimals, symbol, risk metadata, evidence status.
- `pools` — canonical pool identity, protocol/version, token pair, fee tier, tick/range metadata, liquidity/depth observations.
- `pool_observations` — timestamped external observations with provenance.
- `positions` — lifecycle state, pool, principal, range, entry/exit references, timestamps, current reconciliation status.
- `position_events` — append-only lifecycle events.
- `transactions` — requested/submitted/confirmed/reverted chain transactions with hashes and evidence.
- `cashflows` — deposits, withdrawals, swaps, LP principal movements, fees, gas, incentives.
- `fee_events` — fee accrual/collection events with token amounts and valuation evidence.
- `pnl_snapshots` — immutable calculated snapshots used by Telegram rendering.
- `daily_pnl` — derived calendar aggregation keyed by user/date/chain.
- `referrals` / `referral_events` — referral relationships and rewards, isolated from LP PnL.
- `donations` — builder donation records, isolated from LP PnL.
- `audit_events` — security and decision audit trail.
- `decision_runs` — autonomous evaluation inputs, outputs, model versions, evidence references, and gate results.

## Position states

`INITIALIZING`, `SCANNING`, `EVALUATING`, `READY`, `DEPLOYING`, `MONITORING`, `REBALANCING`, `HARVESTING`, `COMPOUNDING`, `EXITING`, `RECONCILING`, `CLOSED`, `PAUSED`, `EMERGENCY`.

## Ledger rules

1. Raw chain observations are immutable evidence.
2. Canonical ledger events are append-only; corrections are compensating events, not destructive edits.
3. Every financial event has asset, raw amount, decimals, valuation source, valuation timestamp, and provenance.
4. Gas is recorded separately and included in net PnL according to accounting policy.
5. Swap costs/slippage are recorded separately from LP fees.
6. Incentives/rewards are separate from trading fees.
7. Realized PnL is recognized only after the position exit has been reconciled.
8. Unrealized PnL is explicitly marked as unrealized and never used as realized history.
9. Telegram output is a view of the ledger, never the ledger itself.
10. A `CONFLICTED` or insufficiently evidenced position cannot trigger a new autonomous deployment.

## Net PnL model

```text
Net Realized PnL
= realized LP fees
+ realized incentives/rewards
+ other realized gains
- divergence / impermanent-loss effect as measured by the accounting model
- gas
- swap costs and slippage
- protocol/platform fees
```

The system must not treat a fixed IL dollar amount as universally valid. IL/divergence is calculated from the position's actual entry/exit amounts and the defined benchmark/accounting methodology.

## One active position

Enforce at the database level and orchestration level that a user has at most one active LP position. Ambiguous chain/application state blocks entry until reconciliation resolves it.

## Idempotency

Every external write and reconciliation event must have an idempotency key. Replayed receipts/events must not double-count principal, fees, gas, or PnL.

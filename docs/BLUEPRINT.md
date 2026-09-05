# Zupin Autonomous LP Agent — Final Blueprint

Status: **PHASE 0 / DESIGN FREEZE CANDIDATE**

## 1. Product contract

Zupin is a Telegram-first autonomous LP agent. The user delegates LP lifecycle decisions; there is **no manual LP trading mode**.

Primary target: Robinhood Chain (EVM, chain ID 4663). EVM/SVM wallet capability is designed at the account layer, but a chain/protocol is executable only after its integration evidence is proven.

Non-negotiables:

- One active LP position per user.
- Autonomous selection, entry, monitoring, rebalance, harvest/compound where supported, and exit.
- Telegram is the control/observability plane, not the source of financial truth.
- Blockchain-backed canonical ledger is the source for position state, cashflows, fees, realized PnL, and closed-position notifications.
- No transaction without simulation/preflight, policy gates, and execution evidence.
- Contradictory, stale, incomplete, or unverified data causes a fail-closed decision.
- Private keys never enter source control, normal logs, analytics, prompts, or Telegram.
- LLM output cannot directly authorize a transaction. Deterministic policy/risk/economic engines own authorization.
- PnL images are presentation artifacts generated from canonical ledger snapshots.

## 2. Final architecture

```text
Telegram Bot / Mini App UI
        |
        v
Application API + Auth + User State
        |
        +--------------------+
        |                    |
        v                    v
Autonomous Orchestrator   Accounting API
        |                    |
        v                    v
Decision Engine          Canonical Ledger
  |  |  |  |                 |
  |  |  |  +-- Risk          +-- PnL Engine
  |  |  +----- Economics     +-- Calendar
  |  +-------- Market Data   +-- Referral Ledger
  +----------- LLM Thesis    +-- Audit Trail
        |
        v
Execution Policy Gate
        |
        v
Transaction Simulator
        |
        v
Signer / Key Management Boundary
        |
        v
Chain Adapters
  |                 |
  +-- EVM/RPC       +-- SVM/RPC
        |
        v
DEX / LP Protocol Adapters
        |
        v
Indexer / Receipt Reconciler
        |
        +----------> Canonical Ledger
```

## 3. Modules

### `domain`
Pure business objects and invariants: users, wallets, pools, positions, transactions, cashflows, fees, PnL snapshots, referrals, audit events.

### `orchestrator`
Autonomous lifecycle state machine. It schedules scans, evaluates candidates, creates bounded decisions, and coordinates execution/reconciliation.

### `market_data`
Read-only adapters for pool, token, price, liquidity, volume, fee, volatility, and protocol metadata. External data must carry provenance and timestamp.

### `strategy`
Candidate scoring and expected-value/risk models. No direct signing capability.

### `risk`
Hard gates: token/protocol allowlists, liquidity/depth, volatility, range probability, concentration, gas, slippage, expected net return, drawdown/stop conditions, cooldowns, and stale-data limits.

### `execution`
Simulation, transaction construction, nonce management, signing request, broadcast, receipt tracking, and idempotency. Every write is evidence-linked.

### `reconciliation`
Reads chain receipts/state and converts observed facts into canonical position/cashflow events. Reconciliation is authoritative for execution outcomes.

### `accounting`
Canonical double-entry-style event ledger plus realized/unrealized PnL views, fee accounting, gas accounting, ROI, and calendar aggregation.

### `wallet`
EVM and SVM address/key lifecycle. Key material is isolated from application business logic and protected by encryption/key-management controls.

### `telegram`
Menu, status, wallet display, PnL calendar, closed-position PnL cards, referral, donation, settings, alerts, and emergency controls. It never calculates authoritative balances itself.

### `rendering`
Deterministic generation of PnL calendar and closed-position images from immutable ledger snapshots.

### `security`
Secret handling, authorization, audit logging, rate limiting, replay/idempotency protection, export controls, and kill-switch behavior.

## 4. Autonomous lifecycle

```text
OFF
 -> INITIALIZING
 -> SCANNING
 -> EVALUATING
 -> READY
 -> DEPLOYING
 -> MONITORING
 -> REBALANCING (optional)
 -> HARVESTING/COMPOUNDING (optional)
 -> EXITING
 -> RECONCILING
 -> CLOSED
 -> SCANNING
```

Any invariant failure can transition to `PAUSED` or `EMERGENCY`.

A position is not `CLOSED` merely because the application requested an exit. It becomes closed only after the chain evidence required by the adapter is confirmed and reconciliation succeeds.

## 5. Decision hierarchy

1. **Safety/integrity gate** — reject on contradictions, stale data, unsupported protocol behavior, failed simulation, or security anomaly.
2. **Economic gate** — expected net return after gas, swap/slippage, protocol/platform fees, expected divergence/IL risk, and incentives.
3. **Risk gate** — liquidity, volatility, token/protocol risk, concentration, range survivability, and exposure limits.
4. **Strategy score** — rank eligible pools.
5. **LLM thesis** — explain why the deterministic result is preferred; never override hard gates.

## 6. One-position invariant

At most one position may be in an economically active state per user. Database uniqueness plus orchestrator locking must enforce this invariant. Reconciliation must resolve ambiguous states before a new deployment is authorized.

## 7. Data provenance

Every external observation records:

- source/provider
- chain ID
- block number when applicable
- observed timestamp
- data timestamp when supplied
- request/correlation ID
- confidence/provenance status

Evidence labels used throughout the project:

- **PROVEN** — directly verified by authoritative documentation, API response, transaction receipt, contract state, or other defined primary evidence.
- **INFERRED** — derived calculation or interpretation from proven inputs.
- **UNKNOWN** — not yet established.
- **CONFLICTED** — two or more evidence sources disagree; execution is blocked until resolved.

## 8. External integration rule

No DEX, protocol, API endpoint, transaction builder, contract address, selector, fee schedule, or chain capability is accepted from memory or assumption.

Implementation evidence priority:

1. Official protocol/chain documentation.
2. Official API/SDK/GitHub repository.
3. Verified deployed contract/source/on-chain state.
4. Official explorer data.
5. Reputable third-party data only as a secondary cross-check.

If evidence is insufficient: mark `UNKNOWN` and keep execution disabled.

## 9. Robinhood Chain boundary

Robinhood Chain is officially documented as an Ethereum L2 with chain ID 4663 and ETH as native gas. The production adapter must still verify the exact DEX contracts, LP mechanics, routers/position managers, supported tokens, and transaction paths before enabling writes.

## 10. PnL presentation

`Canonical Ledger -> PnL Snapshot -> Renderer -> Telegram`

Two first-class renderings:

- Portfolio PnL Calendar: day/week/month views, fees included, chain filter.
- Closed Position PnL Card: pair, protocol/version, deployed capital, returned value, realized fees, gas, swaps/slippage, realized PnL, ROI, open/close timestamps, holding duration, and evidence links.

The renderer must not invent or recompute financial truth from Telegram state.

## 11. Referral and donation accounting

Referral and builder donation are separate ledgers from trading PnL. Referral credits cannot be mixed into LP performance unless explicitly categorized as external rewards.

## 12. Operational boundary

Production deployment requires:

- encrypted secret/key management
- isolated signer boundary
- database backups and migrations
- structured audit logs with secret redaction
- health/reconciliation monitors
- transaction retry/idempotency controls
- emergency pause
- dry-run/testnet mode
- explicit production enablement gate

Phase 0 does **not** enable real-money autonomous execution.

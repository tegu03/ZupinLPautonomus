# Zupin Autonomous LP Agent — Build Roadmap

Status: **SOURCE-OF-TRUTH PHASE OWNERSHIP**

This document formalizes phase ownership for the implementation plan. The existing `BLUEPRINT.md` defines the product architecture and module boundaries; it does **not** itself define a numbered Phase 0–9 roadmap. This document makes that phase mapping explicit so implementation does not drift between phases.

## Phase sequence

| Phase | Name | Primary ownership | Exit condition |
|---|---|---|---|
| 0 | Foundation Contract | Architecture, domain model, accounting contract, Telegram UX contract, security boundary, evidence policy, non-financial skeleton | Foundation is frozen, internally consistent, tested, and no transaction execution is enabled |
| 1 | Chain + Protocol Integration | Robinhood Chain adapter, Uniswap v4 integration, PoolKey/PoolId, StateView, PositionManager simulation, controlled write-route verification | Required chain/protocol capabilities are proven with primary/on-chain evidence and controlled verification |
| 2 | Market Data + Pool Intelligence | Pool discovery, observations, prices, liquidity, volume, fee/volatility inputs, provenance and freshness | Candidate pool data is trustworthy, fresh, provenance-aware, and fail-closed |
| 3 | Strategy + Risk + Economics | Candidate scoring, expected-value model, risk gates, gas/slippage/IL economics, deterministic authorization policy | Strategy decisions are deterministic, testable, and reject unsafe/uneconomic states |
| 4 | Execution Engine | Transaction construction, simulation/preflight, nonce/idempotency, signer boundary, broadcast, receipt tracking | Authorized transactions can be executed and tracked without bypassing policy gates |
| 5 | Autonomous LP Lifecycle | Scan/evaluate/deploy/monitor/rebalance/harvest/compound/exit state machine and one-position orchestration | Autonomous lifecycle works end-to-end under controlled conditions with recovery paths |
| 6 | Reconciliation + Accounting + PnL | Receipt/state reconciliation, canonical ledger, cashflows, fees, realized/unrealized PnL, daily calendar, closed-position accounting | On-chain state and accounting reconcile deterministically; PnL is auditable |
| 7 | Telegram Production | Production bot flows, wallet UX, autonomy controls, status, alerts, PnL views, emergency controls | Telegram is a safe control/observability plane over canonical backend state |
| 8 | Referral + Donation | Referral ledger, attribution, builder donation flow, isolation from LP accounting | Referral/donation accounting is isolated, auditable, and cannot contaminate LP PnL |
| 9 | Production Security + Operations | Secret/key management hardening, monitoring, alerting, rate limits, incident response, kill switch, deployment/backup/recovery | Production security and operational readiness are proven; production launch may be considered |

## Phase 0 — Foundation Contract

Phase 0 owns only the non-financial foundation and contracts:

- final architecture and module boundaries;
- autonomous lifecycle/state-machine contract;
- canonical data model and ledger rules;
- Telegram UX contract;
- wallet/security boundary;
- evidence/source policy;
- PostgreSQL/SQLAlchemy/Alembic foundation;
- domain invariants and tests;
- non-transactional Telegram shell;
- deterministic PnL rendering from fixture/canonical data;
- evidence registry and fail-closed resolution.

Phase 0 does **not** own live chain reads, protocol write-path verification, signer integration, transaction broadcast, autonomous strategy, or real-money execution.

## Phase 1 — Chain + Protocol Integration

Phase 1 owns the protocol-specific groundwork already present in the current implementation branch, including:

- Robinhood Chain capability verification;
- Uniswap v4 deployment verification;
- PoolKey validation and PoolId derivation;
- StateView ABI reads and pool-state validation;
- PositionManager calldata/simulation boundary;
- controlled mint vectors;
- controlled/testnet/forked verification of the exact LP write route, including approvals, simulation, expected state deltas, receipt evidence, and reconciliation.

No Phase 1 artifact is a license to execute user funds. Execution remains disabled until the later execution/security gates are satisfied.

## Phase 2 — Market Data + Pool Intelligence

Build the trustworthy market-data layer used by strategy. Every observation needs provenance, timestamp/block context, freshness rules, and conflict handling. Unknown or conflicting inputs remain non-executable.

## Phase 3 — Strategy + Risk + Economics

Build deterministic pool scoring and economic/risk gates. The LLM may provide thesis/explanation, but it cannot directly authorize transactions. Safety/integrity, economics, and risk gates outrank strategy preference and LLM output.

## Phase 4 — Execution Engine

Build the signer and execution boundary only after chain/protocol capability is proven. Every write must pass policy, simulation/preflight, idempotency, signing, broadcast, receipt tracking, and evidence capture.

## Phase 5 — Autonomous LP Lifecycle

Connect the deterministic decision and execution layers into the autonomous lifecycle. Preserve the one-active-position invariant and fail closed on ambiguous reconciliation.

## Phase 6 — Reconciliation + Accounting + PnL

Make blockchain-backed state and the canonical ledger the financial source of truth. Telegram must never become the source of truth for position state or PnL.

## Phase 7 — Telegram Production

Promote the Telegram shell into a production control/observability interface only after backend state, execution, reconciliation, and accounting are reliable. No financial truth is stored only in Telegram.

## Phase 8 — Referral + Donation

Implement referral and builder-donation accounting as separate ledgers. Neither is allowed to alter LP performance accounting.

## Phase 9 — Production Security + Operations

Complete production hardening, operational controls, monitoring, incident response, backups/recovery, kill switch, and launch readiness. Real-money autonomous execution is still **NO-GO** until all required gates are explicitly satisfied.

## Cross-phase rules

1. Never silently move a deliverable between phases.
2. Existing code can be retained as groundwork even when its phase ownership changes.
3. `PROVEN`, `INFERRED`, `UNKNOWN`, and `CONFLICTED` evidence semantics remain global and non-negotiable.
4. `UNKNOWN` and `CONFLICTED` are fail-closed for autonomous execution.
5. No signer or broadcast capability may bypass the execution policy gate.
6. No phase may claim completion based only on documentation when runtime/on-chain proof is required.
7. Each phase must have explicit tests, audit criteria, and an exit decision before the next phase is treated as active.

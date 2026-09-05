# Phase 0 — Foundation Contract

Status: **IN PROGRESS / NON-FINANCIAL FOUNDATION**

Phase 0 establishes the contract that every later implementation phase must obey. It intentionally does not implement or verify protocol-specific LP execution. Real-money autonomous LP execution is disabled.

Phase ownership is defined centrally in [`ROADMAP.md`](ROADMAP.md). Protocol/chain integration work that already exists on this branch is preserved as implementation material, but it is **owned by Phase 1**, not counted as Phase 0 completion.

## Deliverables

### Specification and architecture

- [x] Final system blueprint.
- [x] Module boundaries.
- [x] Autonomous lifecycle/state machine.
- [x] Canonical data model and ledger rules.
- [x] Telegram UX contract.
- [x] Wallet/security boundary.
- [x] Evidence/source policy.

### Non-financial foundation

- [x] Select production database and migration framework: PostgreSQL + SQLAlchemy + Alembic.
- [x] Implement schema migrations, including append-only database triggers and one-active-position constraint.
- [x] Implement initial domain models and invariant tests.
- [x] Implement Telegram shell without transaction execution.
- [x] Implement deterministic PnL renderer using fixture ledger data.
- [x] Implement integration evidence registry.

### Explicitly deferred to Phase 1+

The following artifacts are **not Phase 0 deliverables**. They may remain in the repository as reviewed groundwork, but they are governed and verified under the later phase that owns them:

- Robinhood Chain connectivity/capability probing.
- Uniswap v4 deployment and contract-address integration.
- PoolKey validation/discovery.
- StateView ABI reading and pool-state verification.
- Deterministic Uniswap v4 PoolId derivation.
- EVM simulation against PositionManager calls.
- Controlled Uniswap v4 mint calldata construction and ABI vectors.
- End-to-end controlled/testnet/forked LP write-route verification.

See [`ROADMAP.md`](ROADMAP.md) and [`PHASE-1.md`](PHASE-1.md).

## Phase 0 completion criteria

Phase 0 is complete when the foundation contract is frozen and independently testable:

1. The repository has a reviewed, versioned specification and explicit phase ownership.
2. Domain invariants have executable tests.
3. Database schema enforces one active LP position per user.
4. Financial events are append-only/idempotent.
5. Secrets are excluded from source control and logs by design.
6. Telegram UI can display wallet, autonomy status, PnL calendar, and closed-position PnL from fixtures/canonical data without performing transactions.
7. PnL image generation is deterministic and traceable to a snapshot ID.
8. Evidence registry can mark integrations `PROVEN`, `INFERRED`, `UNKNOWN`, or `CONFLICTED`.
9. The architecture explicitly prevents transaction execution while required capability evidence is `UNKNOWN` or `CONFLICTED`.
10. CI executes the repository's configured lint/type/test/security checks.
11. No Phase 1+ protocol integration is required to declare the Phase 0 foundation complete.

## Phase gates

### Gate 0A — Specification freeze

Blueprint, data model, UX, security, evidence rules, and phase ownership are reviewed and internally consistent.

### Gate 0B — Non-financial foundation

Database/domain/Telegram/rendering/evidence foundations exist; all transaction execution remains disabled.

### Gate 0C — Phase 0 consistency audit

Cross-document references, module ownership, invariants, and fail-closed rules are consistent. Protocol-specific verification is **not** required for this gate.

### Gate 0D — Foundation CI/security gate

Configured tests and static/security checks pass for the foundation. This gate does not authorize mainnet execution.

Protocol controlled verification and mainnet capability proof belong to Phase 1 and later phases according to [`ROADMAP.md`](ROADMAP.md).

## Development rules for Hermes

Hermes is the implementation executor. It must:

- read these specifications before changing architecture;
- use primary sources for integration facts;
- record evidence for every external capability;
- never invent addresses, selectors, endpoints, fee semantics, or protocol support;
- stop and report `UNKNOWN`/`CONFLICTED` instead of guessing;
- never commit secrets;
- never enable production writes as part of Phase 0;
- add tests for every invariant and bug fix;
- report exact files, tests, and commit/PR identifiers after work.

## Current execution posture

**NO-GO for real-money autonomous LP execution.**

This is deliberate: Phase 0 establishes the foundation only. Production execution remains disabled until the later chain/protocol, market-data, strategy/risk, execution, lifecycle, reconciliation/accounting, Telegram production, and security/operations gates are independently satisfied.

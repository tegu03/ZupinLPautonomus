# Phase 0 — Foundation Contract

Status: **FINAL CANDIDATE / NON-FINANCIAL FOUNDATION**

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
- [x] Explicit phase ownership and Phase 1 handoff.

### Non-financial foundation

- [x] Select production database and migration framework: PostgreSQL + SQLAlchemy + Alembic.
- [x] Implement schema migrations, including append-only database triggers and one-active-position constraint.
- [x] Implement initial domain models and invariant tests.
- [x] Implement Telegram shell without transaction execution.
- [x] Implement deterministic PnL renderer using fixture ledger data.
- [x] Implement integration evidence registry.

## Explicitly deferred to Phase 1+

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

## Phase 0 exit checklist

Phase 0 may be declared **CLOSED** only when every item below is explicitly verified:

### Specification consistency

- [x] `BLUEPRINT.md` defines the product architecture and module boundaries.
- [x] `DATA-MODEL.md` defines canonical entities, position states, ledger rules, PnL model, and one-position invariant.
- [x] `SECURITY.md` defines the key boundary, transaction safety requirements, fail-closed rules, and audit requirements.
- [x] `TELEGRAM-UX.md` defines the control/observability contract without manual LP execution controls.
- [x] `EVIDENCE-POLICY.md` defines evidence states, source hierarchy, and execution blocking semantics.
- [x] `ROADMAP.md` is the explicit source of truth for phase ownership.
- [x] `PHASE-1.md` provides a clear handoff for protocol-specific groundwork and controlled verification.

### Foundation implementation

- [x] Domain invariants have executable tests.
- [x] Database schema enforces one active LP position per user.
- [x] Financial events are append-only/idempotent.
- [x] Telegram foundation is non-transactional.
- [x] PnL rendering is deterministic and traceable to a snapshot ID.
- [x] Evidence registry resolves `PROVEN`, `INFERRED`, `UNKNOWN`, and `CONFLICTED` states fail-closed.
- [x] No Phase 0 component provides a signer or broadcast capability.
- [x] Secrets are excluded from source control/logging by design.

### Safety and phase boundary

- [x] Real-money autonomous execution remains disabled.
- [x] Protocol-specific live/controlled verification is explicitly deferred to Phase 1+.
- [x] `UNKNOWN` and `CONFLICTED` evidence cannot authorize autonomous execution.
- [x] No Phase 1 artifact is being used as evidence that Phase 0 is complete.

### CI gate

- [ ] GitHub Actions CI passes on the final Phase 0 commit.
- [ ] CI executes database migration plus the configured automated test suite.
- [ ] No failing or required-but-missing foundation check remains.

**Important:** Phase 0 CI is a foundation verification gate. A CI pass does not prove Robinhood/Uniswap runtime capability and does not authorize production execution.

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

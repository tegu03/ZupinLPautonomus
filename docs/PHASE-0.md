# Phase 0 — Foundation Contract

Status: **IN PROGRESS / NON-FINANCIAL SKELETON**

Phase 0 establishes the contract that later implementation phases must obey. It intentionally does not enable real-money autonomous LP execution.

## Deliverables

- [x] Final system blueprint.
- [x] Module boundaries.
- [x] Autonomous lifecycle/state machine.
- [x] Canonical data model and ledger rules.
- [x] Telegram UX contract.
- [x] Wallet/security boundary.
- [x] Evidence/source policy.
- [x] Select production database and migration framework: PostgreSQL + SQLAlchemy + Alembic.
- [x] Implement schema migrations, including append-only database triggers and one-active-position constraint.
- [x] Implement initial domain models and invariant tests.
- [x] Implement Telegram shell without transaction execution.
- [x] Implement deterministic PnL renderer using fixture ledger data.
- [x] Implement integration evidence registry.
- [ ] Verify Robinhood protocol capabilities from primary sources/on-chain for executable write paths.

## Current Phase 0 code

The repository contains the non-financial foundation with:

- evidence-state enum (`PROVEN`, `INFERRED`, `UNKNOWN`, `CONFLICTED`);
- explicit autonomous position states;
- one-active-position invariant at domain and PostgreSQL levels;
- append-only/idempotent financial-event storage;
- Telegram control/observability shell with no manual LP transaction controls;
- deterministic PnL calendar PNG renderer traceable to a snapshot ID;
- persistent evidence registry with fail-closed resolution;
- CI configured with PostgreSQL migration execution.

No RPC signer, transaction builder, DEX write adapter, wallet secret handling, or mainnet execution path is enabled in Phase 0.

## Verification status

- Latest feature branch commit: `4d667789cad815e14a0aa4092d090b0201a0dd7d` at the time of this document update.
- GitHub Actions wrapper did not expose a completed run for the latest push commits when checked. Therefore CI is **CONFIGURED but NOT CLAIMED PASS** until a completed run is observable.
- PostgreSQL runtime tests are present and CI now provisions PostgreSQL 16 and runs `alembic upgrade head` before tests.
- Robinhood Chain connectivity is proven by current official documentation: chain ID `4663`, ETH gas, public mainnet RPC, and Blockscout explorer.
- Uniswap official deployment data proves v2/v3/v4-related contracts are deployed on chain `4663`, including PoolManager and Position Manager. This does **not** by itself prove that Zupin's intended autonomous LP write route is safe and executable.
- Executable Robinhood LP write capability remains `UNKNOWN` until the exact write route, pool selection, simulation/preflight behavior, and reconciliation path are verified.

## Definition of done

Phase 0 is complete only when:

1. The repository has a reviewed, versioned specification.
2. Domain invariants have executable tests.
3. Database schema enforces one active LP position per user.
4. Financial events are append-only/idempotent.
5. Secrets are excluded from source control and logs.
6. Telegram UI can display wallet, autonomy status, PnL calendar, and closed-position PnL from fixtures/canonical data without performing transactions.
7. PnL image generation is deterministic and traceable to a snapshot ID.
8. Evidence registry can mark integrations `PROVEN`, `INFERRED`, `UNKNOWN`, or `CONFLICTED`.
9. No write adapter can execute while required capability evidence is `UNKNOWN` or `CONFLICTED`.
10. CI runs lint/type/test/security checks defined by the implementation stack.

## Phase gates

### Gate 0A — Specification

Blueprint, data model, UX, security, and evidence rules reviewed.

### Gate 0B — Non-financial skeleton

Database/domain/Telegram/rendering foundations exist; all transaction execution remains disabled.

### Gate 0C — Testnet verification

Adapters are verified against controlled/testnet fixtures where available. No mainnet user funds.

### Gate 0D — Mainnet capability proof

Every mainnet write capability has primary-source and/or on-chain evidence. Economic and security tests pass.

Only after these gates may a separate production-execution phase be considered.

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

This is deliberate: the system is being built so that production execution is enabled only after LP lifecycle, fee accounting, security, protocol support, and economic evidence are proven.

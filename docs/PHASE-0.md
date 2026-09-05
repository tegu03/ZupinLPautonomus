# Phase 0 — Foundation Contract

Status: **IN PROGRESS / DESIGN + SAFETY FOUNDATION**

Phase 0 establishes the contract that later implementation phases must obey. It intentionally does not enable real-money autonomous LP execution.

## Deliverables

- [x] Final system blueprint.
- [x] Module boundaries.
- [x] Autonomous lifecycle/state machine.
- [x] Canonical data model and ledger rules.
- [x] Telegram UX contract.
- [x] Wallet/security boundary.
- [x] Evidence/source policy.
- [ ] Select production database and migration framework.
- [ ] Implement schema migrations.
- [ ] Implement domain models and invariant tests.
- [ ] Implement Telegram shell without transaction execution.
- [ ] Implement deterministic PnL renderer using fixture ledger data.
- [ ] Implement integration evidence registry.
- [ ] Verify Robinhood protocol capabilities from primary sources/on-chain.

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

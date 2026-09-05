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
- [x] Implement fail-closed EVM simulation boundary for verified Robinhood v4 PositionManager calls (read-only `eth_call` + `eth_estimateGas`; no broadcast).
- [x] Implement fail-closed PoolKey validation/discovery for externally supplied pool observations.
- [x] Implement fail-closed validation of read-only v4 pool state snapshots.
- [x] Implement read-only StateView ABI reader for concrete pool state verification.
- [ ] Verify a concrete Robinhood LP write route end-to-end against a controlled/testnet or forked environment with a verified pool, calldata, approvals, simulation, expected state deltas, and reconciliation.

## Current Phase 0 code

The repository contains the non-financial foundation with:

- evidence-state enum (`PROVEN`, `INFERRED`, `UNKNOWN`, `CONFLICTED`);
- explicit autonomous position states;
- one-active-position invariant at domain and PostgreSQL levels;
- append-only/idempotent financial-event storage;
- Telegram control/observability shell with no manual LP transaction controls;
- deterministic PnL calendar PNG renderer traceable to a snapshot ID;
- persistent evidence registry with fail-closed resolution;
- CI configured with PostgreSQL migration execution;
- read-only Robinhood Chain capability probe;
- read-only EVM simulation boundary restricted to the verified PositionManager `modifyLiquidities(bytes,uint256)` selector and performing `eth_call` plus `eth_estimateGas`;
- fail-closed pool discovery that validates token ordering, fee, tick spacing, hook, source evidence, and latest-observation conflicts;
- pure validation of StateView-style `getSlot0`/`getLiquidity` observations before they can be treated as trusted state evidence;
- read-only StateView ABI reader that calls `getSlot0(bytes32)` and `getLiquidity(bytes32)` and decodes the documented return widths.

No RPC signer, transaction builder, DEX write adapter, wallet secret handling, or mainnet execution path is enabled in Phase 0.

## Verification status

- Robinhood Chain connectivity is proven by current official documentation: chain ID `4663`, ETH gas, public mainnet RPC, and Blockscout.
- Uniswap official deployment data proves v4 contracts are deployed on chain `4663`, including PoolManager and Position Manager. This does **not** by itself prove that Zupin's intended autonomous LP write route is safe and executable.
- Official Uniswap documentation proves the v4 PositionManager uses command-based `modifyLiquidities()` and documents MINT/SETTLE, INCREASE, DECREASE/TAKE, and fee-collection call construction. Zupin deliberately does not hard-code a protocol-specific calldata encoder until a concrete pool and route are independently verified.
- A fail-closed simulation boundary is implemented and rejects non-`modifyLiquidities(bytes,uint256)` selectors. It can simulate an externally encoded PositionManager call with `eth_call` and estimate gas, but it has **not** been run against a controlled Robinhood pool in this repository environment.
- Uniswap's official StateView interface exposes read-only `getSlot0`, `getLiquidity`, and position/fee-growth getters for off-chain pool-state inspection. These reads are suitable as evidence inputs, but they do not themselves authorize a write route. citeturn1search0turn1search1
- The repository now has a read-only StateView reader using verified selectors `getSlot0(bytes32) = 0xc815641c` and `getLiquidity(bytes32) = 0xfa6793d5`; it has unit coverage for ABI encoding/decoding but has **not** yet reached the Robinhood RPC successfully in this environment.
- Pool discovery/validation is implemented for externally supplied evidence, but no concrete production pool is promoted to executable capability by this module alone.
- A secondary ecosystem source identifies a native/USDG Robinhood v4 pool with fee `500`, tickSpacing `10`, no hook, and pool ID `0x387bf619da4d3fb62bb276482693dba1b9b3520f573cabdfe033384a24125982`. This remains **INFERRED/SECONDARY** until independently verified against on-chain state; it must not be hard-coded as an executable production pool.
- Executable Robinhood LP write capability remains `UNKNOWN` until the exact pool, calldata, approvals/Permit2 path, simulation result, expected state delta, and receipt reconciliation are verified.

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

### Gate 0C — Controlled verification

Adapters are verified against controlled/testnet fixtures where available. If Robinhood testnet lacks the required deployment, use a controlled local fork/fixture rather than claiming testnet support. No mainnet user funds.

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

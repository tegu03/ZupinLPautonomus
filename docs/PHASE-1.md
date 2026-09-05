# Phase 1 — Chain + Protocol Integration

Status: **PLANNED / HANDOFF FROM PHASE 0**

Phase 1 owns chain- and protocol-specific capability verification for the initial Robinhood Chain + Uniswap v4 target. It does not authorize production user-fund execution by itself.

## Scope

- Robinhood Chain capability verification.
- Uniswap v4 deployment/address verification.
- PoolKey validation and deterministic PoolId derivation.
- Read-only StateView ABI reads and pool-state validation.
- PositionManager calldata construction and simulation boundary.
- Controlled/testnet/forked verification of the exact LP write route.
- Evidence records for every externally verifiable capability.

## Required controlled verification

Before a write route can be treated as executable capability, verify all of the following in a controlled environment:

1. Correct chain ID and RPC endpoint.
2. Required Uniswap v4 contracts have verified deployed bytecode.
3. Concrete pool metadata is proven from primary/on-chain evidence.
4. PoolId derived from the validated PoolKey matches the observed pool.
5. Pool state is read successfully and passes validation at a known block.
6. Token approval/Permit2 requirements are proven for the selected route.
7. PositionManager calldata is ABI-correct and targets the verified contract.
8. `eth_call` simulation succeeds with expected parameters.
9. Gas estimation succeeds and is sane for the controlled case.
10. Expected balance/position/NFT/state deltas are defined before execution.
11. Controlled execution, if permitted by the test environment, produces the expected receipt and state changes.
12. Receipt/state reconciliation produces canonical evidence.

## Fail-closed rules

- `UNKNOWN` or `CONFLICTED` evidence blocks execution.
- RPC transport failure blocks capability promotion.
- Malformed ABI/RPC data blocks capability promotion.
- Metadata/state disagreement blocks capability promotion.
- A secondary source alone does not promote a production pool to executable status.
- A deterministic calldata fixture does not prove protocol acceptance.
- Simulation success alone does not prove economic safety or production readiness.

## Current handoff material

The current `phase-0/controlled-simulation-harness` branch contains reviewed groundwork for several Phase 1 responsibilities, including read-only Robinhood probing, StateView reads, PoolId derivation, PoolKey/pool-state validation, PositionManager simulation, and a controlled native/USDG mint calldata vector. These artifacts are retained but are not counted toward Phase 0 completion.

## Exit criteria

Phase 1 can close only when the required initial chain/protocol capabilities are marked `PROVEN` with evidence that is sufficient for the next phase. Any unresolved capability remains `UNKNOWN` or `CONFLICTED` and is explicitly carried forward; it is never silently assumed.

Real-money autonomous execution remains disabled until the later execution, lifecycle, accounting, security, and operations phases are independently satisfied.

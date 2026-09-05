# Controlled verification harness

## Purpose

This harness establishes a deterministic, non-broadcast test vector for the
Uniswap v4 PositionManager mint command shape. It is a Gate 0C building block,
not production execution proof.

## Verified protocol shape

The official Uniswap v4 documentation describes PositionManager operations as
command sequences encoded into `modifyLiquidities(bytes,uint256)`. A mint can
use `MINT_POSITION`, `SETTLE_PAIR`, and for native ETH handling `SWEEP`.
The repository therefore encodes the following fixture sequence:

`MINT_POSITION (0x02) -> SETTLE_PAIR (0x0d) -> SWEEP (0x14)`

The repository's simulation boundary still requires the canonical
`modifyLiquidities(bytes,uint256)` selector `0xdd46508f` and never signs or
broadcasts a transaction.

## Fixture

The controlled fixture uses the secondary native/USDG candidate metadata:

- currency0: native ETH sentinel (`address(0)`)
- currency1: USDG `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168`
- fee: `500`
- tick spacing: `10`
- hook: zero address
- derived PoolId:
  `0x387bf619da4d3fb62bb276482693dba1b9b3520f573cabdfe033384a24125982`

This metadata remains **INFERRED/SECONDARY** until independently verified
against on-chain state. The fixture must not be promoted to an executable
production pool solely because its PoolId derives consistently.

## What the harness proves

- PoolKey validation is applied before encoding.
- PoolId is deterministically derived from the PoolKey.
- Command bytes are deterministic.
- The generated call begins with the verified PositionManager selector.
- Native currency requires `value_wei = amount0_max` in this fixture.
- No signer, key material, nonce management, or broadcast capability exists in
the harness.

## What remains unproven

The harness does **not** prove:

1. the candidate pool is initialized on Robinhood mainnet;
2. the PositionManager address contains the expected bytecode at runtime;
3. the encoded mint succeeds against Robinhood state;
4. the required ERC-20 approval/Permit2 state is sufficient;
5. the selected tick range and amounts are economically valid;
6. the expected token and position state deltas occur;
7. receipt events reconcile into the canonical ledger.

## Gate 0C next step

Run this vector through a controlled fork or equivalent deterministic RPC
fixture that supplies the actual PositionManager/PoolManager state. Capture:

`calldata + value -> eth_call -> eth_estimateGas -> expected state delta ->
receipt/event fixture -> reconciliation result`

A successful local fixture is evidence that the software boundary is wired
correctly; it must not be labeled as mainnet capability proof. Mainnet
capability remains `UNKNOWN` until primary/on-chain evidence covers the complete
write lifecycle.

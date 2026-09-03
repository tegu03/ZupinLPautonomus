# Foundation Specification

## 1. Core invariant

The bot's unit of decision is a liquidity position, not a pool APR number.

A position is eligible only when expected net return is positive under conservative assumptions and every hard safety gate passes.

Conceptually:

`expected_net_profit = expected_fee_income + verified_other_income - gas - mandatory_fees - expected_execution_cost - expected_IL_cost - risk_buffer`

The implementation must keep each component separately observable. No opaque profitability score may replace the accounting ledger.

## 2. Network boundary

The production system supports exactly one network:

- Robinhood Chain mainnet
- Chain ID: 4663
- Public RPC: https://rpc.mainnet.chain.robinhood.com

RPC endpoints must be configurable. The public RPC is acceptable for development/read validation but production throughput should use a configured provider.

Any chain ID other than 4663 must fail closed.

## 3. Protocol boundary

Supported LP protocols:

- Uniswap V4
- Uniswap V3

V4 is the primary implementation target. V3 is the secondary implementation target. Other AMMs are out of scope for the initial system.

## 4. Architecture layers

### Layer A — Infrastructure

- RPC client
- chain identity verification
- block/time provider
- retry and timeout policy
- ABI registry
- address registry

### Layer B — Protocol readers

V4:
- PoolManager
- StateView
- PositionManager
- Quoter

V3:
- Factory
- Pool
- NonfungiblePositionManager
- Quoter
- Multicall

Readers are read-only and must be independently testable.

### Layer C — Deterministic math

- price/tick conversion
- tick spacing validation
- liquidity math
- token amount math
- fee-growth math
- range calculations

No floating-point arithmetic for on-chain quantities.

### Layer D — Accounting

Maintain a position ledger containing:

- principal/deposited amounts
- current token balances represented by the position
- collected fees
- uncollected fees
- gas paid
- mandatory protocol/platform costs
- execution costs
- realized PnL
- unrealized PnL
- estimated impermanent loss
- net return

Every accounting value must have a source and timestamp/block reference where applicable.

### Layer E — Strategy

- pool discovery
- liquidity/volume/fee analysis
- fee-rate and fee-velocity estimation
- range selection
- expected holding-period return
- rebalance decision
- exit decision

Strategy output is a proposal. It cannot directly broadcast a transaction.

### Layer F — Risk gates

Hard gates run before any live transaction:

- correct chain
- valid pool
- valid token metadata
- valid price/state freshness
- no known security rejection
- sufficient wallet balance
- sufficient allowance/Permit2 state
- gas estimate available and fresh
- mandatory costs known
- expected net return above configured threshold
- maximum execution-cost rule satisfied
- position/range constraints valid

If any hard gate is unknown, the default is reject.

### Layer G — Execution

Execution is isolated from strategy.

The execution layer must:

1. receive an already-approved transaction intent
2. rebuild/verify calldata
3. re-check chain and economic gates
4. simulate when supported
5. sign only when explicitly enabled
6. broadcast
7. wait for receipt/finality policy
8. reconcile on-chain state

No strategy module may contain private-key signing logic.

### Layer H — Autonomous lifecycle

State machine:

`DISCOVERED -> ANALYZED -> APPROVED -> ENTERING -> ACTIVE -> REBALANCE_PENDING -> REBALANCING -> EXIT_PENDING -> EXITING -> CLOSED`

Error/recovery states must be explicit. There must be no implicit transition caused by an exception.

## 5. V4 position model

Do not infer custom storage layouts from failed calls.

The canonical V4 PositionManager interface uses:

- `modifyLiquidities(bytes,uint256)`
- `modifyLiquiditiesWithoutUnlock(bytes,bytes[])`
- `nextTokenId()`
- `getPositionLiquidity(uint256)`
- `getPoolAndPositionInfo(uint256)`
- `positionInfo(uint256)`

`PositionInfo` is a packed `uint256` containing subscriber state, tickLower, tickUpper, and a truncated pool identifier. The exact packing must be implemented from the canonical Uniswap V4 library and covered by round-trip tests.

V4 StateView reads must use its actual interface, including `getSlot0`, `getLiquidity`, `getFeeGrowthGlobals`, `getFeeGrowthInside`, and position-read methods where applicable.

## 6. V3 position model

V3 positions are ERC-721 positions managed by the NonfungiblePositionManager. Pool state must be read from canonical V3 pool interfaces.

Fee accounting must use the pool's fee-growth state and the position's fee-growth-inside checkpoints/tokens owed rather than frontend APR values.

## 7. Fee accounting invariant

For every supported version, the system must be able to answer:

- what fee growth existed at entry
- what fee growth exists now
- how much liquidity was active/in-range
- how much fee is attributable to the position
- what has already been collected
- what remains uncollected

A position cannot enter autonomous management if this reconciliation is not deterministic.

## 8. Cost policy

The economic engine must calculate net execution cost from verified components:

`net_execution_cost = gas_cost + mandatory_platform_fee + mandatory_other_costs - verified_refund`

Unverified refunds are never subtracted.

The configured maximum cost policy is currently **$1.20 net execution cost** per required transaction. This value is a strategy/risk configuration, not a hardcoded assumption inside protocol adapters.

If cost cannot be estimated reliably, the transaction is rejected.

## 9. Data freshness

Every market/state input has a maximum age. Stale state must not be used for a live decision.

Block number and retrieval timestamp are recorded with critical reads.

## 10. Testing gates

Before enabling live execution:

- unit tests for all deterministic math
- ABI/selector tests for all protocol readers
- integration tests against Robinhood Chain
- fee-accounting reconciliation tests
- transaction calldata encoding tests
- simulation/revert tests
- restart/recovery tests
- position lifecycle tests
- economic gate tests
- security gate tests

A passing test count alone is not sufficient. Tests must cover the actual Robinhood deployment addresses and interfaces.

## 11. Git/VPS workflow

GitHub is the source of truth.

Recommended deployment flow:

`GitHub main -> VPS git pull -> install/update dependencies -> run migrations if required -> run tests -> restart service`

Production changes should be committed in small, reviewable units. Secrets are never committed.

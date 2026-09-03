# Real Market Case: HOTDOG LP Farming — 2026-09-03

## Purpose

This document records a real market observation supplied by the user and makes it an explicit strategy test case for the Robinhood Chain autonomous LP bot.

This is **not** a claim of profitability and is **not** authoritative on-chain data. The source was user screenshots from the Zenith LP Telegram interface and a DEX Screener volume chart.

## Network and protocol boundary

- Network: Robinhood Chain mainnet
- Chain ID: `4663`
- Protocol: Uniswap V4
- V3 remains secondary
- No other chain or AMM is introduced by this test case

## Observed pool candidates

| Rank | Pair | Fee | TVL | 24h volume | Volume/TVL | Displayed APR |
|---:|---|---:|---:|---:|---:|---:|
| 1 | HOTDOG/USDG | 4.00% | $212.1K | $2.08M | 9.81x | 14,310% |
| 2 | HOTDOG/USDG | 3.34% | $65.8K | $301.2K | 4.58x | 5,583% |
| 3 | HOTDOG/ETH | 0.90% | $31.8K | $2.92M | **91.82x** | 30,200% |
| 4 | HOTDOG/USDG | 10.00% | $12.0K | $269.8K | 22.48x | 82,225% |
| 5 | HOTDOG/USDG | 3.89% | $11.4K | $3.1K | 0.27x | 390.3% |
| 6 | HOTDOG/USDG | 3.90% | $10.0K | $2.9K | 0.29x | 418.3% |
| 7 | HOTDOG/USDG | 3.91% | $9.9K | $16.9K | 1.71x | 2,429% |
| 8 | HOTDOG/USDG | 4.00% | $4.0K | $577.33 | 0.14x | 211.1% |
| 9 | HOTDOG/WETH | 10.00% | $3.7K | $10.5K | 2.84x | 10,462% |

The displayed APR is retained only as an observed UI field. It must never be treated as the bot's profitability input.

## Gas observation

The user clarified that the observed `~$1` figure is **gas cost per transaction**, not swap-fee income.

For strategy testing:

- observed gas: approximately `$1/TX`
- this is an empirical stress-test value
- it must **not** be hardcoded as production gas
- live decisions must use a fresh gas estimate and current ETH/USD conversion
- lifecycle economics must account for every required transaction: entry, rebalance, collect when applicable, and exit

The current production policy in `config/robinhood.json` remains a maximum configured **$1.20 net execution cost** per required transaction. The empirical `$1/TX` observation is evidence for testing the sensitivity of that policy, not a replacement for live gas estimation.

## Primary strategy test candidate

### HOTDOG/ETH — Uniswap V4 — 0.90%

Observed:

- TVL: approximately `$31.8K`
- 24h volume: approximately `$2.92M`
- volume/TVL: approximately `91.82x`
- displayed APR: approximately `30,200%`
- observed gas: approximately `$1/TX`

This candidate should receive **high observation priority**, but it must not automatically enter LP.

The reason is asymmetric:

- high volume relative to TVL can imply strong fee opportunity;
- low TVL also means liquidity depth is thin and price/range risk can be high;
- concentrated liquidity only earns fees while the position is active in the relevant price range;
- frequent rebalancing can consume fee income through transaction costs.

Therefore the bot must optimize **expected net fee capture after lifecycle costs and risk**, not raw APR.

## Required decision sequence

```text
DISCOVER
  -> VERIFY POOL
  -> READ CURRENT V4 STATE
  -> ESTIMATE FEE VELOCITY
  -> ESTIMATE VOLATILITY
  -> SIMULATE RANGES
  -> ESTIMATE FEE CAPTURE
  -> ESTIMATE IL / RANGE RISK
  -> ESTIMATE LIFECYCLE GAS
  -> ECONOMIC GATE
  -> ENTER or WAIT
```

After entry:

```text
ACTIVE
  -> measure actual fee growth
  -> measure range occupancy
  -> estimate future fee opportunity
  -> compare transaction cost vs expected benefit
  -> HOLD / REBALANCE / COLLECT / EXIT
```

## Gas-aware rebalance rule

A rebalance must not happen merely because price moved outside a nominal percentage threshold.

The strategy must compare the incremental benefit of rebalancing against the full incremental transaction cost:

```text
rebalance only when:

expected_additional_fee_capture
  - expected_IL_change
  - expected_slippage
  - expected_rebalance_gas
  - risk_buffer
>
minimum_required_net_benefit
```

If the expected benefit does not clear the threshold, **HOLD**.

This prevents a high-frequency rebalance loop from destroying otherwise positive fee income.

## Fee accounting requirement

The test case must ultimately reconcile real V4 position fee growth rather than infer earnings from APR or pool-wide volume.

For an active position the accounting layer must preserve:

- entry fee-growth checkpoint
- current fee growth inside the selected ticks
- position liquidity
- fees attributable to the position
- collected fees
- uncollected fees
- gas paid
- execution costs
- realized/unrealized PnL

The empirical market observation is therefore a **strategy fixture**, while on-chain V4 state remains the authority for actual accounting.

## Acceptance criteria for this case

The autonomous engine passes this case only if it can:

1. rank HOTDOG/ETH 0.90% highly without blindly entering;
2. distinguish pool-wide volume from position-level fee capture;
3. treat `$1/TX` as a gas observation, not as swap-fee income;
4. calculate lifecycle transaction costs;
5. simulate multiple candidate ranges;
6. account for out-of-range probability and volatility;
7. avoid unnecessary rebalances when transaction cost exceeds expected incremental benefit;
8. reconcile predicted fees against actual V4 fee-growth state;
9. fail closed when gas, state, position, or fee accounting is unknown;
10. remain strictly on Robinhood Chain `4663` and Uniswap V4 for this primary test case.

## Source artifact

Machine-readable fixture:

`data/observations/2026-09-03_hotdog_lp_real_market.json`

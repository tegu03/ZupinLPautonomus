# Robinhood LP Autonomous

Autonomous liquidity-provision research and execution system for **Robinhood Chain only (chain ID 4663)**.

## Objective

Find Uniswap V3/V4 liquidity positions with positive expected **net fee farming return** after gas, mandatory platform/protocol costs, expected impermanent-loss risk, and execution costs.

The system must optimize for **net economics**, not APR displayed by a frontend.

## Scope

- Network: Robinhood Chain mainnet, chain ID 4663
- Primary protocols: Uniswap V4 and Uniswap V3
- Primary objective: fee income minus all relevant costs and risk
- Operation modes: discovery, analysis, shadow/paper, and live execution
- Live execution is disabled by default

## Non-goals

- No multi-chain support
- No automatic deployment to other networks
- No profitability guarantees
- No live trading until all safety and accounting gates pass

## Development principle

Build from verified on-chain primitives upward:

1. Chain/RPC foundation
2. Protocol address registry
3. Token and pool identity
4. V3/V4 state readers
5. Tick/range math
6. Fee-growth accounting
7. Position accounting
8. Cost/gas accounting
9. Net-profit model
10. Security/risk gates
11. Shadow mode
12. Execution
13. Autonomous lifecycle

Every layer must have deterministic tests before the next layer depends on it.

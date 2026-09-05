# Zupin Autonomous LP Agent

Telegram-first autonomous LP farming system.

This repository is a **clean-room rebuild**. GitHub is the source of truth; Hermes is the implementation executor; architecture and review are governed by the versioned specifications in `docs/`.

## Build roadmap

The numbered implementation phases are formally defined in [Build Roadmap](docs/ROADMAP.md). `BLUEPRINT.md` remains the architectural/product contract; `ROADMAP.md` defines phase ownership and exit sequencing.

## Phase 0 — Foundation

Phase 0 establishes the final architecture, canonical ledger model, Telegram UX, wallet/security boundaries, evidence policy, database/domain foundation, and non-transactional UI/rendering foundations. **Real-money autonomous execution is disabled.**

- [Final Blueprint](docs/BLUEPRINT.md)
- [Build Roadmap](docs/ROADMAP.md)
- [Data Model](docs/DATA-MODEL.md)
- [Telegram UX](docs/TELEGRAM-UX.md)
- [Security Contract](docs/SECURITY.md)
- [Evidence & Source Policy](docs/EVIDENCE-POLICY.md)
- [Phase 0 Contract](docs/PHASE-0.md)

## Phase 1 — Chain + Protocol Integration

Phase 1 owns Robinhood Chain and Uniswap v4 capability verification, pool/state verification, PositionManager simulation, and controlled LP write-route verification. Existing implementation groundwork is retained on the integration branch and is not counted as Phase 0 completion.

- [Phase 1 Handoff](docs/PHASE-1.md)

## Engineering principle

No hallucinated integrations. External capabilities must be proven from primary sources and/or verified on-chain evidence before implementation is allowed to execute them.

Evidence states: `PROVEN` / `INFERRED` / `UNKNOWN` / `CONFLICTED`.

`UNKNOWN` and `CONFLICTED` are fail-closed states for autonomous execution.

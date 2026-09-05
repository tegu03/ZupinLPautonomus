# Zupin Autonomous LP Agent

Telegram-first autonomous LP farming system.

This repository is a **clean-room rebuild**. GitHub is the source of truth; Hermes is the implementation executor; architecture and review are governed by the versioned specifications in `docs/`.

## Phase 0

Phase 0 establishes the final architecture, canonical ledger model, Telegram UX, wallet/security boundaries, and evidence policy. **Real-money autonomous execution is disabled.**

- [Final Blueprint](docs/BLUEPRINT.md)
- [Data Model](docs/DATA-MODEL.md)
- [Telegram UX](docs/TELEGRAM-UX.md)
- [Security Contract](docs/SECURITY.md)
- [Evidence & Source Policy](docs/EVIDENCE-POLICY.md)
- [Phase 0 Contract](docs/PHASE-0.md)

## Engineering principle

No hallucinated integrations. External capabilities must be proven from primary sources and/or verified on-chain evidence before implementation is allowed to execute them.

Evidence states: `PROVEN` / `INFERRED` / `UNKNOWN` / `CONFLICTED`.

`UNKNOWN` and `CONFLICTED` are fail-closed states for autonomous execution.

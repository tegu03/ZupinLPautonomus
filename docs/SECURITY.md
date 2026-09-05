# Security Contract

Status: **PHASE 0**

## Threat model

Protect user funds and signing authority against:

- source-control leaks
- `.env`/backup/log leakage
- Telegram disclosure
- compromised application process
- replay/double execution
- malicious or misconfigured protocol adapters
- stale/contradictory market data
- prompt injection or LLM hallucination
- unauthorized autonomous actions

## Key boundary

Business services must never receive raw private keys as ordinary application data.

Preferred production boundary:

```text
Autonomous Decision
      |
      v
Policy Gate
      |
      v
Transaction Intent
      |
      v
Signer Boundary / KMS
      |
      v
Signed Transaction
      |
      v
Broadcast
```

For development/testnet, local keypairs may be used only in isolated test environments and must never be committed.

## EVM/SVM wallet model

A user has one logical Zupin account with separate chain-specific addresses/key references:

```text
user
 ├── evm_wallet
 └── svm_wallet
```

The system must not assume an EVM private key can sign Solana transactions or vice versa. Solana uses Ed25519 keypairs; EVM uses the signing model of its compatible account type.

## Export policy

Private-key export is a high-risk operation. If enabled, it requires explicit user confirmation, short-lived exposure, audit logging of the event (without the secret), and automatic Telegram cleanup. The secret itself is never written to application logs, databases, analytics, prompts, or source control.

## Transaction safety

Before broadcast:

1. Verify user/agent authorization.
2. Verify position state and one-position invariant.
3. Verify adapter capability and evidence status.
4. Verify balances and allowances/state prerequisites.
5. Simulate where the chain/protocol supports it.
6. Validate minimum output, slippage, gas ceiling, and economic gates.
7. Create an idempotency key.
8. Sign only inside the signer boundary.
9. Broadcast once.
10. Track receipt and reconcile before advancing state.

## Fail-closed rules

Block execution on:

- `CONFLICTED` evidence
- stale critical observations
- unknown contract/selector/transaction path
- failed simulation
- unexpected balance/state delta
- nonce conflict not safely resolved
- exceeded gas/slippage/risk limits
- duplicate active position
- signer authorization anomaly

## Audit events

Record actor, action, decision ID, policy version, evidence IDs, transaction hash when available, result, and timestamps. Never record private keys, seed phrases, signing payload secrets, or provider credentials.

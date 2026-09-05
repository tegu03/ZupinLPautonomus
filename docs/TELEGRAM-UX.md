# Telegram UX Contract

Status: **PHASE 0**

Telegram is the user's control and observability plane. There is no manual LP execution mode.

## `/start`

1. Resolve/create Zupin user.
2. Provision logical wallet record and display public addresses only.
3. Show the main menu.
4. Never expose seed/private-key material during onboarding.

## Main menu

```text
🤖 LP Autonomous Agent
💰 Balance / Wallet
📊 PnL Calendar
👥 Referrals
❤️ Donate to Builder
⚙️ Settings
🆘 Help Center
```

The exact button layout may evolve, but autonomous LP remains the primary action.

## Autonomous Agent screen

Show:

- autonomy status
- current position or `No active position`
- selected pool/protocol
- deployed capital
- current position value
- accrued fees
- estimated net PnL
- range/status information when applicable
- last evidence/reconciliation timestamp
- current decision state
- concise `Why this position?` explanation

Do not present a user button that directly performs LP entry/exit. Autonomous policy owns those actions.

## PnL Calendar

Clicking `📊 PnL Calendar` renders a deterministic image from `daily_pnl`/`pnl_snapshots`.

Views:

- Day
- Week
- Month
- Prev / Next
- Chain filter

Calendar values represent realized, evidence-backed daily movement according to the accounting policy. Fees are included where the view specifies them.

## Closed Position PnL

After an autonomous exit is confirmed and reconciled, send a closed-position PnL card/image containing:

- protocol + version
- token pair
- fee tier when applicable
- open timestamp
- close timestamp
- holding duration
- capital deployed
- capital returned
- LP fees realized
- incentives realized
- gas
- swap/slippage costs
- realized net PnL
- ROI
- transaction/explorer references

A normal `position closed` notification is forbidden until required on-chain execution evidence and reconciliation are present.

## Wallet screen

Show public EVM/SVM addresses and balances. Dust tokens can be categorized as hidden/unpriced, but never silently included in PnL.

### Key export

If product policy eventually allows export:

- require explicit confirmation
- generate a short-lived disclosure
- never persist the plaintext key
- never log it
- never include it in analytics/error traces
- delete the Telegram message as soon as the security window expires
- use Telegram's current ephemeral-message capability where appropriate and supported

Telegram's API supports message deletion and, in current Bot API versions, ephemeral messages; deletion is not a guarantee against screenshots, copying, cached clients, or offline delivery. The implementation must therefore treat Telegram deletion as exposure reduction, not cryptographic erasure.

## Errors

User-visible errors must expose a safe status such as:

`Execution blocked — evidence is incomplete/CONFLICTED. No funds were moved.`

Never reveal secrets, internal stack traces, raw provider credentials, or unsigned sensitive payloads.

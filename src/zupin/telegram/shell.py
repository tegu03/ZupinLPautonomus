from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MainMenu:
    rows: tuple[tuple[str, ...], ...] = (
        ("🤖 LP Autonomous Agent",),
        ("💰 Balance / Wallet", "📊 PnL Calendar"),
        ("👥 Referrals", "❤️ Donate to Builder"),
        ("⚙️ Settings", "🆘 Help Center"),
    )


class TelegramShell:
    """Render Telegram UI state without exposing transaction controls."""

    def __init__(self, menu: MainMenu | None = None) -> None:
        self.menu = menu or MainMenu()

    def menu_markup(self) -> dict[str, object]:
        return {"keyboard": [list(row) for row in self.menu.rows], "resize_keyboard": True}

    def welcome_text(self) -> str:
        return (
            "Welcome to Zupin.\n\n"
            "Autonomous LP is the primary mode. Zupin controls LP actions through its "
            "autonomous policy; Telegram does not provide manual LP execution."
        )

    def agent_text(
        self,
        *,
        autonomy_status: str,
        position: str = "No active position",
        pool: str = "Unknown",
        deployed_capital: str = "Unknown",
        position_value: str = "Unknown",
        accrued_fees: str = "Unknown",
        estimated_net_pnl: str = "Unknown",
        range_status: str = "Unknown",
        evidence_timestamp: str = "Unknown",
        decision_state: str = "Unknown",
        thesis: str = "No verified position thesis available.",
    ) -> str:
        return (
            "🤖 LP Autonomous Agent\n\n"
            f"Autonomy: {autonomy_status}\n"
            f"Position: {position}\n"
            f"Pool / Protocol: {pool}\n"
            f"Deployed capital: {deployed_capital}\n"
            f"Current value: {position_value}\n"
            f"Accrued fees: {accrued_fees}\n"
            f"Estimated net PnL: {estimated_net_pnl}\n"
            f"Range / status: {range_status}\n"
            f"Last evidence / reconciliation: {evidence_timestamp}\n"
            f"Decision state: {decision_state}\n\n"
            f"Why this position?\n{thesis}"
        )

    def wallet_text(
        self,
        *,
        evm_address: str | None,
        svm_address: str | None,
        balances: str = "Balance data unavailable.",
    ) -> str:
        evm = evm_address or "Not provisioned"
        svm = svm_address or "Not provisioned"
        return f"💰 Balance / Wallet\n\nEVM: {evm}\nSVM: {svm}\n\n{balances}"

    def pnl_calendar_text(self) -> str:
        return (
            "📊 PnL Calendar\n\n"
            "Deterministic calendar rendering is being prepared from canonical ledger "
            "snapshots. No transaction is performed from this screen."
        )

    def referrals_text(self) -> str:
        return "👥 Referrals\n\nReferral accounting is isolated from LP performance accounting."

    def donation_text(self) -> str:
        return "❤️ Donate to Builder\n\nDonations are accounted for separately from LP PnL."

    def settings_text(self) -> str:
        return "⚙️ Settings\n\nAutonomous policy and notification settings."

    def help_text(self) -> str:
        return (
            "🆘 Help Center\n\n"
            "Zupin is autonomous: there is no manual LP entry/exit button.\n"
            "If execution evidence is incomplete or conflicted, execution is blocked."
        )

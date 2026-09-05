from zupin.telegram.shell import TelegramShell


def test_main_menu_matches_ux_contract() -> None:
    shell = TelegramShell()
    buttons = [button for row in shell.menu.rows for button in row]
    assert buttons == [
        "🤖 LP Autonomous Agent",
        "💰 Balance / Wallet",
        "📊 PnL Calendar",
        "👥 Referrals",
        "❤️ Donate to Builder",
        "⚙️ Settings",
        "🆘 Help Center",
    ]


def test_shell_never_exposes_manual_lp_controls() -> None:
    shell = TelegramShell()
    rendered = shell.agent_text(autonomy_status="OFF")
    assert "manual" not in rendered.lower()
    assert "entry" not in rendered.lower()
    assert "exit" not in rendered.lower()


def test_wallet_renderer_shows_public_addresses_only() -> None:
    shell = TelegramShell()
    rendered = shell.wallet_text(evm_address="0x123", svm_address="So111")
    assert "0x123" in rendered
    assert "So111" in rendered
    assert "private" not in rendered.lower()
    assert "seed" not in rendered.lower()

from __future__ import annotations

import asyncio
from typing import Any, Callable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from zupin.db.models import User, Wallet

from .api import TelegramBotApi
from .shell import TelegramShell


SessionFactory = sessionmaker[Session]


class TelegramApp:
    """Phase 0 Telegram application; deliberately has no transaction handlers."""

    def __init__(self, api: TelegramBotApi, session_factory: SessionFactory) -> None:
        self.api = api
        self.session_factory = session_factory
        self.shell = TelegramShell()

    def provision_user(self, telegram_user_id: int) -> tuple[User, Wallet]:
        with self.session_factory() as session:
            user = session.scalar(select(User).where(User.telegram_user_id == telegram_user_id))
            if user is None:
                user = User(telegram_user_id=telegram_user_id)
                session.add(user)
                try:
                    session.flush()
                except IntegrityError:
                    session.rollback()
                    user = session.scalar(select(User).where(User.telegram_user_id == telegram_user_id))
                    if user is None:
                        raise
            wallet = session.scalar(select(Wallet).where(Wallet.user_id == user.id))
            if wallet is None:
                wallet = Wallet(user_id=user.id)
                session.add(wallet)
            session.commit()
            session.refresh(user)
            session.refresh(wallet)
            return user, wallet

    def handle_update(self, update: dict[str, Any]) -> None:
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if not isinstance(chat_id, int):
            return
        text = str(message.get("text") or "").strip()
        telegram_user = message.get("from") or {}
        telegram_user_id = telegram_user.get("id")
        if not isinstance(telegram_user_id, int):
            return

        if text.startswith("/start"):
            user, wallet = self.provision_user(telegram_user_id)
            wallet_note = "Logical wallet record provisioned. Public addresses are not available yet." if not wallet.evm_address and not wallet.svm_address else ""
            response = self.shell.welcome_text()
            if wallet_note:
                response += f"\n\n{wallet_note}"
            self.api.send_message(chat_id, response, reply_markup=self.shell.menu_markup())
            return

        handlers: dict[str, Callable[[], str]] = {
            "🤖 LP Autonomous Agent": lambda: self.shell.agent_text(autonomy_status="OFF"),
            "💰 Balance / Wallet": lambda: self.shell.wallet_text(evm_address=None, svm_address=None),
            "📊 PnL Calendar": self.shell.pnl_calendar_text,
            "👥 Referrals": self.shell.referrals_text,
            "❤️ Donate to Builder": self.shell.donation_text,
            "⚙️ Settings": self.shell.settings_text,
            "🆘 Help Center": self.shell.help_text,
        }
        handler = handlers.get(text)
        if handler is not None:
            self.api.send_message(chat_id, handler(), reply_markup=self.shell.menu_markup())
            return

        self.api.send_message(chat_id, "Unknown command. Use the menu below.", reply_markup=self.shell.menu_markup())

    async def run_polling(self) -> None:
        offset: int | None = None
        while True:
            updates = await asyncio.to_thread(self.api.get_updates, offset=offset)
            for update in updates:
                update_id = update.get("update_id")
                if isinstance(update_id, int):
                    offset = update_id + 1
                self.handle_update(update)

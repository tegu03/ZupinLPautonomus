from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib import parse, request


@dataclass(frozen=True)
class TelegramApiError(RuntimeError):
    description: str


class TelegramBotApi:
    """Small stdlib-only Telegram Bot API client for the Phase 0 shell."""

    def __init__(self, token: str | None = None, *, timeout: float = 30.0) -> None:
        self._token = token or os.getenv("ZUPIN_TELEGRAM_BOT_TOKEN")
        if not self._token:
            raise RuntimeError("ZUPIN_TELEGRAM_BOT_TOKEN is required")
        self._timeout = timeout
        self._base_url = f"https://api.telegram.org/bot{self._token}/"

    def call(self, method: str, payload: dict[str, object] | None = None) -> dict[str, object]:
        body = parse.urlencode(payload or {}).encode("utf-8")
        req = request.Request(self._base_url + method, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with request.urlopen(req, timeout=self._timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not data.get("ok"):
            raise TelegramApiError(str(data.get("description", "Telegram API error")))
        return data["result"]

    def get_updates(self, *, offset: int | None = None, timeout: int = 25) -> list[dict[str, object]]:
        payload: dict[str, object] = {"timeout": timeout, "allowed_updates": json.dumps(["message", "callback_query"])}
        if offset is not None:
            payload["offset"] = offset
        result = self.call("getUpdates", payload)
        return list(result)

    def send_message(self, chat_id: int, text: str, *, reply_markup: dict[str, object] | None = None) -> dict[str, object]:
        payload: dict[str, object] = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = json.dumps(reply_markup, separators=(",", ":"))
        return self.call("sendMessage", payload)

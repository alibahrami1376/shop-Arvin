"""HTTP client for Bale Bot API (wallet invoices)."""

from __future__ import annotations

import json
import logging
from typing import Any

import requests

from payment.bale_config import get_bale_config

logger = logging.getLogger(__name__)


class BaleAPIError(Exception):
    def __init__(self, message: str, *, response: dict | None = None):
        super().__init__(message)
        self.response = response or {}


def toman_to_rial(amount_toman) -> int:
    return int(amount_toman) * 10


class BaleClient:
    def __init__(
        self,
        bot_token: str | None = None,
        provider_token: str | None = None,
        api_base: str | None = None,
    ):
        cfg = get_bale_config()
        self.bot_token = bot_token if bot_token is not None else cfg.bot_token
        self.provider_token = (
            provider_token if provider_token is not None else cfg.provider_token
        )
        self.api_base = (api_base or cfg.api_base).rstrip("/")
        self._cfg = cfg

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token)

    def _url(self, method: str) -> str:
        return f"{self.api_base}/bot{self.bot_token}/{method}"

    def api(self, method: str, **params: Any) -> dict:
        if not self.bot_token:
            raise BaleAPIError("توکن ربات بله تنظیم نشده است")
        try:
            response = requests.post(self._url(method), json=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.exception("Bale API request failed: %s", method)
            raise BaleAPIError(str(exc)) from exc

        if not data.get("ok"):
            raise BaleAPIError(
                data.get("description") or "Bale API error",
                response=data,
            )
        return data.get("result")

    def send_message(self, chat_id, text: str) -> dict:
        return self.api("sendMessage", chat_id=chat_id, text=text)

    def send_invoice(
        self,
        *,
        chat_id,
        title: str,
        description: str,
        payload: str,
        prices: list[dict],
        provider_token: str | None = None,
        photo_url: str | None = None,
    ) -> dict:
        params: dict[str, Any] = {
            "chat_id": chat_id,
            "title": title[:32],
            "description": description[:255],
            "payload": payload[:128],
            "provider_token": provider_token or self.provider_token,
            "prices": prices,
        }
        if photo_url:
            params["photo_url"] = photo_url
        try:
            return self.api("sendInvoice", **params)
        except BaleAPIError:
            params["prices"] = json.dumps(prices, ensure_ascii=False)
            return self.api("sendInvoice", **params)

    def answer_pre_checkout_query(
        self,
        pre_checkout_query_id: str,
        ok: bool,
        error_message: str | None = None,
    ) -> bool:
        params: dict[str, Any] = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok,
        }
        if not ok and error_message:
            params["error_message"] = error_message
        return bool(self.api("answerPreCheckoutQuery", **params))

    def inquire_transaction(self, transaction_id: str) -> dict:
        return self.api("inquireTransaction", transaction_id=transaction_id)

    def set_webhook(self, url: str) -> dict:
        return self.api("setWebhook", url=url)

    def get_webhook_info(self) -> dict:
        return self.api("getWebhookInfo")

    def delete_webhook(self) -> dict:
        return self.api("deleteWebhook")

    def build_deep_link(self, start_token: str) -> str:
        cfg = self._cfg
        username = (cfg.bot_username or "").lstrip("@")
        base = cfg.deep_link_base.rstrip("/")
        if not username:
            return ""
        return f"{base}/{username}?start={start_token}"

"""Resolve Bale bot config from admin DB only (no env for bot/wallet secrets)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

DEFAULT_API_BASE = "https://tapi.bale.ai"
DEFAULT_DEEP_LINK_BASE = "https://ble.ir"
DEFAULT_LINK_TTL_MINUTES = 60


@dataclass(frozen=True)
class BaleConfig:
    bot_token: str
    provider_token: str
    bot_username: str
    webhook_secret: str
    api_base: str
    deep_link_base: str
    link_token_ttl_minutes: int

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.bot_username)


def get_bale_config() -> BaleConfig:
    """All bot/wallet settings come from BaleBotSettings in the database."""
    from payment.models import BaleBotSettings

    try:
        row = BaleBotSettings.get_solo()
    except Exception:
        return BaleConfig(
            bot_token="",
            provider_token="",
            bot_username="",
            webhook_secret="",
            api_base=DEFAULT_API_BASE,
            deep_link_base=DEFAULT_DEEP_LINK_BASE,
            link_token_ttl_minutes=DEFAULT_LINK_TTL_MINUTES,
        )

    api_base = (row.api_base or "").strip() or DEFAULT_API_BASE
    deep_link = (row.deep_link_base or "").strip() or DEFAULT_DEEP_LINK_BASE
    ttl = int(row.link_token_ttl_minutes or DEFAULT_LINK_TTL_MINUTES)
    return BaleConfig(
        bot_token=(row.bot_token or "").strip(),
        provider_token=(row.provider_token or "").strip(),
        bot_username=(row.bot_username or "").strip().lstrip("@"),
        webhook_secret=(row.webhook_secret or "").strip(),
        api_base=api_base.rstrip("/"),
        deep_link_base=deep_link.rstrip("/"),
        link_token_ttl_minutes=ttl,
    )


def build_bale_webhook_url(secret: str | None = None) -> str:
    """
    Public webhook URL for setWebhook.

    Domain/protocol come from site settings (SITE_DOMAIN / Sites / SSL) —
    those remain developer/env concerns. Secret comes from admin DB.
    """
    from payment.zarinpal_client import get_domain, get_protocol

    cfg = get_bale_config()
    sec = (secret if secret is not None else cfg.webhook_secret) or ""
    path = "/payment/bale/bot-webhook/"
    query = urlencode({"secret": sec}) if sec else ""
    base = f"{get_protocol()}://{get_domain()}{path}"
    return f"{base}?{query}" if query else base

from unittest.mock import patch

from accounts.models import User, UserType
from django.test import TestCase
from django.urls import reverse

from payment.bale_config import get_bale_config
from payment.models import BaleBotSettings


class BaleAdminSettingsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_customer(
            email="bale-admin@example.com",
            password="pass12345",
            type=UserType.admin.value,
            is_staff=True,
            is_active=True,
            is_verified=True,
        )
        self.settings_row = BaleBotSettings.get_solo()

    def test_get_bale_config_from_db_only(self):
        self.settings_row.bot_token = "db-token"
        self.settings_row.bot_username = "db_bot"
        self.settings_row.provider_token = "db-provider"
        self.settings_row.webhook_secret = "db-secret"
        self.settings_row.save()
        cfg = get_bale_config()
        self.assertEqual(cfg.bot_token, "db-token")
        self.assertEqual(cfg.bot_username, "db_bot")
        self.assertEqual(cfg.provider_token, "db-provider")
        self.assertEqual(cfg.webhook_secret, "db-secret")

    def test_get_bale_config_empty_when_db_empty(self):
        cfg = get_bale_config()
        self.assertEqual(cfg.bot_token, "")
        self.assertEqual(cfg.bot_username, "")
        self.assertEqual(cfg.api_base, "https://tapi.bale.ai")
        self.assertEqual(cfg.deep_link_base, "https://ble.ir")

    def test_form_preserves_token_when_blank(self):
        self.settings_row.bot_token = "keep-me"
        self.settings_row.webhook_secret = "keep-secret"
        self.settings_row.bot_username = "old_user"
        self.settings_row.save()

        self.client.force_login(self.admin)
        url = reverse("dashboard:admin:bale-bot-settings")
        resp = self.client.post(
            url,
            {
                "action": "save",
                "bot_token": "",
                "webhook_secret": "",
                "provider_token": "WALLET-TEST-1111111111111111",
                "bot_username": "@new_bot",
                "api_base": "https://tapi.bale.ai",
                "deep_link_base": "https://ble.ir",
                "link_token_ttl_minutes": "90",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.settings_row.refresh_from_db()
        self.assertEqual(self.settings_row.bot_token, "keep-me")
        self.assertEqual(self.settings_row.webhook_secret, "keep-secret")
        self.assertEqual(self.settings_row.bot_username, "new_bot")
        self.assertEqual(self.settings_row.link_token_ttl_minutes, 90)

    @patch("dashboard.admin.views.bale_bot_settings.BaleClient")
    def test_set_webhook_action(self, client_cls):
        self.settings_row.bot_token = "tok"
        self.settings_row.webhook_secret = "sec"
        self.settings_row.bot_username = "shopbot"
        self.settings_row.save()
        client_cls.return_value.set_webhook.return_value = {"url": "https://x/y"}

        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("dashboard:admin:bale-bot-settings"),
            {"action": "set_webhook"},
        )
        self.assertEqual(resp.status_code, 302)
        client_cls.return_value.set_webhook.assert_called_once()
        called_url = client_cls.return_value.set_webhook.call_args.args[0]
        self.assertIn("/payment/bale/bot-webhook/", called_url)
        self.assertIn("secret=sec", called_url)

    @patch("dashboard.admin.views.bale_bot_settings.BaleClient")
    def test_get_webhook_info_action(self, client_cls):
        self.settings_row.bot_token = "tok"
        self.settings_row.save()
        client_cls.return_value.get_webhook_info.return_value = {"url": "https://x"}

        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("dashboard:admin:bale-bot-settings"),
            {"action": "get_webhook_info"},
        )
        self.assertEqual(resp.status_code, 302)
        client_cls.return_value.get_webhook_info.assert_called_once()

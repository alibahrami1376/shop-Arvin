from datetime import timedelta
from unittest.mock import MagicMock, patch

from accounts.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from order.models import OrderModel, OrderStatusType
from order.services.payment import PaymentService

from payment.bale_client import toman_to_rial
from payment.bale_webhook import (
    handle_pre_checkout_query,
    handle_start,
    handle_successful_payment,
)
from payment.models import PaymentMethodType, PaymentModel, PaymentStatusType
from payment.services import inquire_transaction_matches_payment, mark_payment_success


@override_settings(
    BALE_BOT_TOKEN="test-bot-token",
    BALE_PROVIDER_TOKEN="WALLET-TEST-1111111111111111",
    BALE_BOT_USERNAME="arvin_bot",
    BALE_WEBHOOK_SECRET="whsec",
    BALE_LINK_TOKEN_TTL_MINUTES=60,
)
class BalePaymentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_customer(
            email="bale-buyer@example.com",
            password="pass12345",
        )
        self.order = OrderModel.objects.create(
            user=self.user,
            address="addr",
            state="Tehran",
            city="Tehran",
            zip_code="1234567890",
            total_price=100000,
        )

    def _create_bale_payment(self, *, amount=100000, expired=False, authority=None):
        payment = PaymentModel.objects.create(
            authority_id=authority or "bale-test-authority-1",
            amount=amount,
            method=PaymentMethodType.bale.value,
            link_token=f"tok_{PaymentModel.objects.count()}",
            link_token_expires_at=timezone.now()
            + (timedelta(minutes=-5) if expired else timedelta(minutes=30)),
            response_json={},
        )
        self.order.payment = payment
        self.order.save(update_fields=["payment"])
        return payment

    def test_toman_to_rial(self):
        self.assertEqual(toman_to_rial(100000), 1_000_000)

    def test_create_bale_payment_url(self):
        url = PaymentService().create_bale_payment_url(self.order)
        self.order.refresh_from_db()
        pay = self.order.payment
        self.assertIsNotNone(pay)
        self.assertEqual(pay.method, PaymentMethodType.bale.value)
        self.assertTrue(pay.authority_id.startswith("bale-"))
        self.assertTrue(pay.link_token)
        self.assertTrue(pay.is_link_token_valid())
        self.assertIn(f"/order/bale-payment/{self.order.pk}/", url)

    @patch("payment.bale_webhook.BaleClient")
    def test_start_sends_invoice(self, client_cls):
        payment = self._create_bale_payment()
        client = client_cls.return_value
        client.send_invoice.return_value = {"message_id": 42}

        handle_start(
            {"chat": {"id": 999}, "text": f"/start {payment.link_token}"},
            f"/start {payment.link_token}",
        )

        client.send_invoice.assert_called_once()
        kwargs = client.send_invoice.call_args.kwargs
        self.assertEqual(kwargs["payload"], payment.authority_id)
        self.assertEqual(kwargs["prices"][0]["amount"], payment.amount_rial)
        payment.refresh_from_db()
        self.assertEqual(payment.bale_chat_id, "999")
        self.assertEqual(payment.bale_invoice_message_id, 42)

    @patch("payment.bale_webhook.BaleClient")
    def test_start_rejects_expired_token(self, client_cls):
        payment = self._create_bale_payment(expired=True)
        client = client_cls.return_value
        handle_start(
            {"chat": {"id": 1}, "text": f"/start {payment.link_token}"},
            f"/start {payment.link_token}",
        )
        client.send_invoice.assert_not_called()
        client.send_message.assert_called()

    @patch("payment.bale_webhook.BaleClient")
    def test_start_locks_chat_id(self, client_cls):
        payment = self._create_bale_payment()
        payment.bale_chat_id = "111"
        payment.save(update_fields=["bale_chat_id"])
        client = client_cls.return_value

        handle_start(
            {"chat": {"id": 222}, "text": f"/start {payment.link_token}"},
            f"/start {payment.link_token}",
        )
        client.send_invoice.assert_not_called()
        payment.refresh_from_db()
        self.assertEqual(payment.bale_chat_id, "111")

    @patch("payment.bale_webhook.BaleClient")
    def test_pre_checkout_rejects_wrong_amount(self, client_cls):
        payment = self._create_bale_payment(amount=50000)
        client = client_cls.return_value
        handle_pre_checkout_query(
            {
                "id": "pcq-1",
                "invoice_payload": payment.authority_id,
                "total_amount": 999,
                "currency": "IRR",
                "from": {"id": 1},
            }
        )
        payment.refresh_from_db()
        self.assertEqual(payment.bale_pre_checkout_id, "pcq-1")
        client.answer_pre_checkout_query.assert_called_once_with(
            "pcq-1", False, error_message="مبلغ صورتحساب با سفارش مطابقت ندارد."
        )

    @patch("payment.bale_webhook.BaleClient")
    def test_pre_checkout_ok_even_if_link_expired(self, client_cls):
        payment = self._create_bale_payment(expired=True)
        payment.bale_chat_id = "7"
        payment.save(update_fields=["bale_chat_id"])
        client = client_cls.return_value
        handle_pre_checkout_query(
            {
                "id": "pcq-exp",
                "invoice_payload": payment.authority_id,
                "total_amount": payment.amount_rial,
                "currency": "IRR",
                "from": {"id": 7},
            }
        )
        client.answer_pre_checkout_query.assert_called_once_with(
            "pcq-exp", True, error_message=None
        )
        payment.refresh_from_db()
        self.assertEqual(payment.bale_pre_checkout_id, "pcq-exp")

    @patch("payment.bale_webhook.BaleClient")
    def test_pre_checkout_ok(self, client_cls):
        payment = self._create_bale_payment()
        payment.bale_chat_id = "5"
        payment.save(update_fields=["bale_chat_id"])
        client = client_cls.return_value
        handle_pre_checkout_query(
            {
                "id": "pcq-2",
                "invoice_payload": payment.authority_id,
                "total_amount": payment.amount_rial,
                "currency": "IRR",
                "from": {"id": 5},
            }
        )
        client.answer_pre_checkout_query.assert_called_once_with(
            "pcq-2", True, error_message=None
        )
        payment.refresh_from_db()
        self.assertEqual(payment.bale_pre_checkout_id, "pcq-2")

    @patch("payment.bale_webhook.BaleClient")
    def test_successful_payment_idempotent(self, client_cls):
        payment = self._create_bale_payment()
        payment.bale_chat_id = "7"
        payment.save(update_fields=["bale_chat_id"])
        client_cls.return_value.send_message = MagicMock()
        msg = {
            "chat": {"id": 7},
            "successful_payment": {
                "currency": "IRR",
                "total_amount": payment.amount_rial,
                "invoice_payload": payment.authority_id,
                "telegram_payment_charge_id": "chg-1",
                "provider_payment_charge_id": "prov-1",
            },
        }
        handle_successful_payment(msg)
        handle_successful_payment(msg)

        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatusType.preparing.value)
        self.assertEqual(self.order.status, OrderStatusType.success.value)
        self.assertEqual(payment.bale_telegram_payment_charge_id, "chg-1")

    @patch("payment.bale_webhook.BaleClient")
    def test_successful_payment_ignores_expired_link(self, client_cls):
        payment = self._create_bale_payment(expired=True)
        payment.bale_chat_id = "7"
        payment.save(update_fields=["bale_chat_id"])
        client_cls.return_value.send_message = MagicMock()
        handle_successful_payment(
            {
                "chat": {"id": 7},
                "successful_payment": {
                    "currency": "IRR",
                    "total_amount": payment.amount_rial,
                    "invoice_payload": payment.authority_id,
                    "telegram_payment_charge_id": "chg-exp",
                },
            }
        )
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatusType.preparing.value)

    def test_mark_payment_success_idempotent(self):
        payment = self._create_bale_payment()
        self.assertTrue(mark_payment_success(payment))
        self.assertFalse(mark_payment_success(payment))

    def test_webhook_requires_secret(self):
        client = Client()
        url = reverse("payment:bale-bot-webhook")
        resp = client.post(url, data=b"{}", content_type="application/json")
        self.assertEqual(resp.status_code, 403)

        resp = client.post(
            url + "?secret=whsec",
            data=b'{"update_id":1}',
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_webhook_rejects_when_secret_empty(self):
        with override_settings(BALE_WEBHOOK_SECRET=""):
            resp = Client().post(
                reverse("payment:bale-bot-webhook"),
                data=b"{}",
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 403)

    def test_inquire_match_helper(self):
        payment = self._create_bale_payment()
        payment.bale_chat_id = "9"
        payment.bale_pre_checkout_id = "pcq-x"
        payment.save(update_fields=["bale_chat_id", "bale_pre_checkout_id"])
        self.assertTrue(
            inquire_transaction_matches_payment(
                {
                    "id": "pcq-x",
                    "status": "paid",
                    "amount": payment.amount_rial,
                    "userID": 9,
                },
                payment,
            )
        )
        self.assertFalse(
            inquire_transaction_matches_payment(
                {
                    "id": "pcq-x",
                    "status": "paid",
                    "amount": 1,
                    "userID": 9,
                },
                payment,
            )
        )

    @patch("order.views.BaleClient")
    def test_inquire_marks_paid(self, client_cls):
        payment = self._create_bale_payment()
        payment.bale_telegram_payment_charge_id = "chg-inq"
        payment.bale_chat_id = "3"
        payment.save(update_fields=["bale_telegram_payment_charge_id", "bale_chat_id"])
        client_cls.return_value.inquire_transaction.return_value = {
            "id": "chg-inq",
            "status": "paid",
            "amount": payment.amount_rial,
            "userID": 3,
        }

        self.client.force_login(self.user)
        url = reverse("order:bale-payment-inquire", kwargs={"pk": self.order.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatusType.preparing.value)

    @patch("order.views.BaleClient")
    def test_inquire_network_error_keeps_awaiting(self, client_cls):
        from payment.bale_client import BaleAPIError

        payment = self._create_bale_payment()
        payment.bale_pre_checkout_id = "pcq-net"
        payment.save(update_fields=["bale_pre_checkout_id"])
        client_cls.return_value.inquire_transaction.side_effect = BaleAPIError("down")

        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("order:bale-payment-inquire", kwargs={"pk": self.order.pk})
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "awaiting")
        self.assertEqual(data["inquire"], "error")
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatusType.awaiting_payment.value)

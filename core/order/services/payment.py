import secrets
import uuid
from datetime import timedelta

from django.urls import reverse_lazy
from django.utils import timezone
from payment.models import PaymentMethodType, PaymentModel
from payment.zarinpal_client import ZarinPalSandbox


class PaymentService:
    def start_payment(self, *, order, payment_method: int) -> str:
        if payment_method == PaymentMethodType.card_to_card.value:
            return self.create_card_payment_url(order)
        if payment_method == PaymentMethodType.bale.value:
            return self.create_bale_payment_url(order)
        if payment_method == PaymentMethodType.gateway.value:
            return self.create_gateway_payment_url(order)
        raise ValueError(f"Unsupported payment method: {payment_method}")

    def create_gateway_payment_url(self, order) -> str:
        zarinpal = ZarinPalSandbox()
        response = zarinpal.payment_request(order.get_price())
        authority = response["Authority"]
        payment_obj = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.get_price(),
            method=PaymentMethodType.gateway.value,
            response_json=response,
        )
        order.payment = payment_obj
        order.save()
        return zarinpal.generate_payment_url(authority)

    def create_card_payment_url(self, order) -> str:
        authority = f"card-{order.pk}-{uuid.uuid4().hex}"
        payment_obj = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.get_price(),
            method=PaymentMethodType.card_to_card.value,
            response_json={},
        )
        order.payment = payment_obj
        order.save()
        return str(
            reverse_lazy("order:card-payment-instructions", kwargs={"pk": order.pk})
        )

    def create_bale_payment_url(self, order) -> str:
        from payment.bale_config import get_bale_config

        ttl = get_bale_config().link_token_ttl_minutes
        authority = f"bale-{uuid.uuid4().hex}"
        link_token = secrets.token_urlsafe(16)
        payment_obj = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.get_price(),
            method=PaymentMethodType.bale.value,
            response_json={},
            link_token=link_token,
            link_token_expires_at=timezone.now() + timedelta(minutes=ttl),
        )
        order.payment = payment_obj
        order.save()
        return str(
            reverse_lazy("order:bale-payment-instructions", kwargs={"pk": order.pk})
        )

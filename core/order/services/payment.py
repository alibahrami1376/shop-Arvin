import uuid

from django.urls import reverse_lazy
from payment.models import PaymentMethodType, PaymentModel
from payment.zarinpal_client import ZarinPalSandbox


class PaymentService:
    def start_payment(self, *, order, payment_method: int) -> str:
        if payment_method == PaymentMethodType.card_to_card.value:
            return self.create_card_payment_url(order)
        return self.create_gateway_payment_url(order)

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

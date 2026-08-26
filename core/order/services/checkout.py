import uuid

from cart.cart import CartSession
from django.db import transaction
from django.urls import reverse_lazy
from payment.models import PaymentMethodType, PaymentModel
from payment.zarinpal_client import ZarinPalSandbox

from order.pricing import apply_pricing_to_order
from order.repositories import order_repo


class CheckoutService:
    def __init__(self, order_repository=None):
        self.order_repo = order_repository or order_repo

    def place_order(self, *, user, cleaned_data, cart, session) -> str:
        coupon = cleaned_data["coupon"]
        payment_method = cleaned_data["payment_method"]

        with transaction.atomic():
            order = self.order_repo.create(
                user=user,
                province=cleaned_data["freight_province"],
                city=cleaned_data["freight_city"],
                freight_notes=cleaned_data["freight_notes"],
            )
            self.order_repo.create_items(order=order, cart=cart)
            self.apply_coupon(coupon=coupon, order=order, user=user)

            coupon_percent = coupon.discount_percent if coupon else 0
            apply_pricing_to_order(order, coupon_percent=coupon_percent)

            session["last_order_tracking_code"] = order.tracking_code

            if payment_method == PaymentMethodType.card_to_card.value:
                redirect_url = self.create_card_payment_next_url(order)
            else:
                redirect_url = self.create_gateway_payment_url(order)

        self.clear_cart(cart=cart, session=session)
        return str(redirect_url)

    def apply_coupon(self, *, coupon, order, user) -> None:
        if not coupon:
            return
        order.coupon = coupon
        coupon.used_by.add(user)
        coupon.save()

    def clear_cart(self, *, cart, session) -> None:
        cart.cart_items.all().delete()
        CartSession(session).clear()

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

    def create_card_payment_next_url(self, order) -> str:
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

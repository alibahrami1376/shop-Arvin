from cart.cart import CartSession
from django.db import transaction

from order.pricing import apply_pricing_to_order
from order.repositories import order_repo
from order.services.payment import PaymentService


class CheckoutService:
    def __init__(self, order_repository=None, payment_service=None):
        self.order_repo = order_repository or order_repo
        self.payment_service = payment_service or PaymentService()

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
            redirect_url = self.payment_service.start_payment(
                order=order,
                payment_method=payment_method,
            )

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

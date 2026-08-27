from cart.cart import CartSession
from django.db import transaction
from payment.models import PaymentMethodSettings

from order.pricing import apply_pricing_to_order, get_checkout_pricing_context
from order.repositories import location_repo, order_repo
from order.services.payment import PaymentService
from order.shipping import FREIGHT_NOTES_PLACEHOLDER


class CheckoutService:
    def __init__(
        self,
        order_repository=None,
        payment_service=None,
        location_repository=None,
    ):
        self.order_repo = order_repository or order_repo
        self.payment_service = payment_service or PaymentService()
        self.location_repo = location_repository or location_repo

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

    def get_checkout_page_context(self, *, user) -> dict:
        from cart.models import CartModel

        cart = CartModel.objects.get(user=user)
        items_subtotal = cart.calculate_total_price()
        pricing = get_checkout_pricing_context(
            items_subtotal,
            city="",
            state="",
        )
        payment_settings = PaymentMethodSettings.get_solo()
        enabled_methods = payment_settings.get_enabled_methods()
        return {
            **pricing,
            "checkout_pricing_json": {
                "tehran_amount": pricing["checkout_pricing"].shipping_tehran_amount,
                "province_amount": pricing["checkout_pricing"].shipping_province_amount,
                "shipping_enabled": pricing["checkout_pricing"].shipping_enabled,
                "tax_enabled": pricing["checkout_pricing"].tax_enabled,
                "tax_percent": pricing["checkout_pricing"].tax_percent,
            },
            "enabled_payment_methods": enabled_methods,
            "payment_methods_available": bool(enabled_methods),
            "freight_provinces": self.location_repo.get_active_provinces(),
            "freight_cities_by_province": (
                self.location_repo.get_active_cities_by_province()
            ),
            "freight_notes_placeholder": FREIGHT_NOTES_PLACEHOLDER,
        }

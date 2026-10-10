import json
from typing import Any

from django.shortcuts import render
from django.views.generic import TemplateView, View
from shop.models import ProductModel, ProductStatusType

from .cart import CartSession


def _cart_page_context(request, cart: CartSession) -> dict[str, Any]:
    return {
        "cart_items": cart.get_cart_items(),
        "total_quantity": cart.get_total_quantity(),
        "total_payment_price": cart.get_total_payment_amount(),
    }


def _htmx_cart_summary_response(request, cart: CartSession):
    return render(
        request,
        "cart/partials/cart-summary-fragment.html",
        _cart_page_context(request, cart),
    )


def _htmx_cart_badges_response(
    request, cart: CartSession, *, toast: dict | None = None
):
    response = render(
        request,
        "cart/partials/cart-badges-oob.html",
        {"total_quantity": cart.get_total_quantity()},
    )
    if toast:
        response["HX-Trigger"] = json.dumps({"showToast": toast})
    return response


class SessionAddProductView(View):
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity", 1)
        if (
            product_id
            and ProductModel.objects.filter(
                id=product_id, status=ProductStatusType.publish.value
            ).exists()
        ):
            cart.add_product(str(product_id), quantity)
        if request.user.is_authenticated:
            cart.persist_to_db(request.user)
        return _htmx_cart_badges_response(
            request,
            cart,
            toast={
                "text": "محصول به سبد خرید اضافه شد",
                "className": "success",
                "background": "#2e7d32",
                "duration": 2500,
            },
        )


class SessionRemoveProductView(View):
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        if product_id:
            cart.remove_product(product_id)
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)
        return _htmx_cart_summary_response(request, cart)


class SessionUpdateProductQuantityView(View):
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")
        if product_id and quantity:
            cart.update_product_quantity(product_id, quantity)
        if request.user.is_authenticated:
            cart.persist_to_db(request.user)
        return _htmx_cart_summary_response(request, cart)


class CartSummaryView(TemplateView):
    template_name = "cart/cart-summary.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        cart = CartSession(self.request.session)
        if self.request.user.is_authenticated:
            cart.ensure_user_cart(self.request.user)
        context.update(_cart_page_context(self.request, cart))
        return context

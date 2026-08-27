from cart.models import CartModel
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, TemplateView, View
from payment.models import (
    CardToCardSettings,
    PaymentMethodSettings,
    PaymentMethodType,
    PaymentStatusType,
)
from payment.zarinpal_client import ZarinPalRequestFailed

from order.forms import CheckOutForm, OrderTrackingForm
from order.models import OrderModel
from order.permissions import HasCustomerAccessPermission
from order.pricing import get_checkout_pricing_context
from order.repositories import order_repo
from order.services import CouponValidationError, checkout_service, coupon_service


class OrderCheckOutView(LoginRequiredMixin, HasCustomerAccessPermission, FormView):
    template_name = "order/checkout.html"
    form_class = CheckOutForm
    success_url = reverse_lazy("order:completed")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        cart = CartModel.objects.get(user=user)
        try:
            redirect_url = checkout_service.place_order(
                user=user,
                cleaned_data=form.cleaned_data,
                cart=cart,
                session=self.request.session,
            )
        except ZarinPalRequestFailed as exc:
            messages.error(self.request, str(exc))
            return redirect(reverse_lazy("order:checkout"))
        return redirect(redirect_url)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartModel.objects.get(user=self.request.user)
        items_subtotal = cart.calculate_total_price()
        context.update(
            get_checkout_pricing_context(
                items_subtotal,
                city="",
                state="",
            )
        )
        context["checkout_pricing_json"] = {
            "tehran_amount": context["checkout_pricing"].shipping_tehran_amount,
            "province_amount": context["checkout_pricing"].shipping_province_amount,
            "shipping_enabled": context["checkout_pricing"].shipping_enabled,
            "tax_enabled": context["checkout_pricing"].tax_enabled,
            "tax_percent": context["checkout_pricing"].tax_percent,
        }
        payment_settings = PaymentMethodSettings.get_solo()
        context["enabled_payment_methods"] = payment_settings.get_enabled_methods()
        context["payment_methods_available"] = bool(context["enabled_payment_methods"])
        from order.models import City, Province
        from order.shipping import FREIGHT_NOTES_PLACEHOLDER

        provinces = list(Province.objects.filter(is_active=True).values("id", "name"))
        cities_by_province = {}
        for city in City.objects.filter(
            is_active=True, province__is_active=True
        ).values("id", "name", "province_id"):
            cities_by_province.setdefault(city["province_id"], []).append(
                {"id": city["id"], "name": city["name"]}
            )
        context["freight_provinces"] = provinces
        context["freight_cities_by_province"] = cities_by_province
        context["freight_notes_placeholder"] = FREIGHT_NOTES_PLACEHOLDER
        return context


class OrderCompletedView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/completed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        code = self.request.session.pop("last_order_tracking_code", None)
        context["tracking_code"] = code
        if code:
            context["tracking_url"] = f"{reverse('order:track')}?code={code}"
        return context


class OrderTrackingView(FormView):
    template_name = "order/tracking.html"
    form_class = OrderTrackingForm

    def get_initial(self):
        code = (self.request.GET.get("code") or "").strip()
        if code:
            return {"tracking_code": code}
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = getattr(self, "tracked_order", None)
        return context

    def get(self, request, *args, **kwargs):
        code = (request.GET.get("code") or "").strip()
        if code:
            self.tracked_order = self._get_order(code)
            if self.tracked_order is None:
                form = self.get_form()
                form.add_error(
                    "tracking_code",
                    "سفارشی با این کد سفارش یافت نشد.",
                )
                return self.render_to_response(self.get_context_data(form=form))
            form = self.form_class(initial={"tracking_code": code})
            return self.render_to_response(self.get_context_data(form=form))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        code = form.cleaned_data["tracking_code"]
        self.tracked_order = self._get_order(code)
        if self.tracked_order is None:
            form.add_error(
                "tracking_code",
                "سفارشی با این کد سفارش یافت نشد.",
            )
            return self.form_invalid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def _get_order(self, code):
        return order_repo.get_by_tracking_code(code)


class OrderFailedView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/failed.html"


class CardPaymentInstructionsView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    """راهنمای واریز کارت به کارت پس از ثبت سفارش."""

    model = OrderModel
    template_name = "order/card-payment-instructions.html"
    context_object_name = "order"

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user).select_related(
            "payment"
        )

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        pay = order.payment
        if pay is None or pay.method != PaymentMethodType.card_to_card.value:
            raise Http404()
        if pay.status != PaymentStatusType.awaiting_payment.value:
            raise Http404()
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cfg = CardToCardSettings.get_solo()
        context["card_bank_name"] = cfg.bank_name
        context["card_holder"] = cfg.account_holder
        context["card_number"] = cfg.card_number
        context["card_iban"] = cfg.iban
        context["card_note"] = cfg.note
        context["receipt_social_links"] = cfg.get_receipt_social_links()
        return context


class ValidateCouponView(LoginRequiredMixin, HasCustomerAccessPermission, View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get("code")
        user = request.user

        try:
            coupon = coupon_service.get_valid_coupon(code=code, user=user)
        except CouponValidationError as exc:
            return JsonResponse({"message": exc.message}, status=exc.status_code)

        cart = CartModel.objects.get(user=user)
        pricing_ctx = get_checkout_pricing_context(
            cart.calculate_total_price(),
            city=(request.POST.get("city") or "").strip(),
            state=(request.POST.get("state") or "").strip(),
            coupon_percent=coupon.discount_percent,
        )
        return JsonResponse(
            {
                "message": "کد تخفیف با موفقیت ثبت شد",
                "subtotal": pricing_ctx["subtotal"],
                "discount_amount": pricing_ctx["discount_amount"],
                "shipping_amount": pricing_ctx["shipping_amount"],
                "total_tax": pricing_ctx["total_tax"],
                "total_price": pricing_ctx["grand_total"],
                "coupon_percent": coupon.discount_percent,
            },
            status=200,
        )

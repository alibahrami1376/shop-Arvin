import uuid

from cart.cart import CartSession
from cart.models import CartModel
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, TemplateView, View
from payment.models import (
    CardToCardSettings,
    PaymentMethodSettings,
    PaymentMethodType,
    PaymentModel,
    PaymentStatusType,
)
from payment.zarinpal_client import ZarinPalRequestFailed, ZarinPalSandbox

from order.forms import CheckOutForm, OrderTrackingForm
from order.models import CouponModel, OrderItemModel, OrderModel
from order.permissions import HasCustomerAccessPermission
from order.pricing import apply_pricing_to_order, get_checkout_pricing_context
from order.shipping import ShippingMethodType


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
        cleaned_data = form.cleaned_data
        coupon = cleaned_data["coupon"]

        cart = CartModel.objects.get(user=user)
        payment_method = cleaned_data["payment_method"]
        try:
            with transaction.atomic():
                order = self.create_order(cleaned_data)
                self.create_order_items(order, cart)
                self.apply_coupon(coupon, order, user)
                coupon_percent = coupon.discount_percent if coupon else 0
                apply_pricing_to_order(order, coupon_percent=coupon_percent)
                self.request.session["last_order_tracking_code"] = order.tracking_code
                if payment_method == PaymentMethodType.card_to_card.value:
                    redirect_url = self._create_card_payment_next_url(order)
                else:
                    redirect_url = self._create_gateway_payment_url(order)
        except ZarinPalRequestFailed as exc:
            messages.error(self.request, str(exc))
            return redirect(reverse_lazy("order:checkout"))

        self.clear_cart(cart)
        return redirect(redirect_url)

    def _create_gateway_payment_url(self, order):
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

    def _create_card_payment_next_url(self, order):
        authority = f"card-{order.pk}-{uuid.uuid4().hex}"
        payment_obj = PaymentModel.objects.create(
            authority_id=authority,
            amount=order.get_price(),
            method=PaymentMethodType.card_to_card.value,
            response_json={},
        )
        order.payment = payment_obj
        order.save()
        return reverse_lazy("order:card-payment-instructions", kwargs={"pk": order.pk})

    def create_order(self, cleaned_data):
        user = self.request.user
        province = cleaned_data["freight_province"]
        city = cleaned_data["freight_city"]
        return OrderModel.objects.create(
            user=user,
            shipping_method=ShippingMethodType.freight.value,
            state=province.name,
            city=city.name,
            address="-",
            zip_code="-",
            freight_notes=cleaned_data["freight_notes"],
        )

    def create_order_items(self, order, cart):
        for item in cart.cart_items.all():
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_price(),
            )

    def clear_cart(self, cart):
        cart.cart_items.all().delete()
        CartSession(self.request.session).clear()

    def apply_coupon(self, coupon, order, user):
        if coupon:
            order.coupon = coupon
            coupon.used_by.add(user)
            coupon.save()

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
        return (
            OrderModel.objects.filter(tracking_code=code)
            .select_related("payment")
            .prefetch_related("order_items__product")
            .first()
        )


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
        user = self.request.user

        status_code = 200
        message = "کد تخفیف با موفقیت ثبت شد"
        total_price = 0
        total_tax = 0
        pricing_ctx = {}

        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            return JsonResponse({"message": "کد تخفیف یافت نشد"}, status=404)
        else:
            if coupon.used_by.count() >= coupon.max_limit_usage:
                status_code, message = (
                    403,
                    "ظرفیت استفاده از این کد تخفیف تکمیل شده است.",
                )

            elif coupon.expiration_date and coupon.expiration_date < timezone.now():
                status_code, message = 403, "کد تخفیف منقضی شده است"

            elif user in coupon.used_by.all():
                status_code, message = 403, "این کد تخفیف قبلا توسط شما استفاده شده است"

            else:
                cart = CartModel.objects.get(user=self.request.user)
                items_subtotal = cart.calculate_total_price()
                city = (request.POST.get("city") or "").strip()
                state = (request.POST.get("state") or "").strip()
                pricing_ctx = get_checkout_pricing_context(
                    items_subtotal,
                    city=city,
                    state=state,
                    coupon_percent=coupon.discount_percent,
                )
                total_tax = pricing_ctx["total_tax"]
                total_price = pricing_ctx["grand_total"]
        return JsonResponse(
            {
                "message": message,
                "subtotal": pricing_ctx.get("subtotal", 0) if status_code == 200 else 0,
                "discount_amount": pricing_ctx.get("discount_amount", 0)
                if status_code == 200
                else 0,
                "shipping_amount": pricing_ctx.get("shipping_amount", 0)
                if status_code == 200
                else 0,
                "total_tax": total_tax,
                "total_price": total_price,
                "coupon_percent": coupon.discount_percent if status_code == 200 else 0,
            },
            status=status_code,
        )

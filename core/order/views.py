import json
import logging

from cart.models import CartModel
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, TemplateView, View
from payment.bale_client import BaleAPIError, BaleClient
from payment.models import (
    CardToCardSettings,
    PaymentMethodType,
    PaymentStatusType,
)
from payment.services import (
    inquire_transaction_matches_payment,
    mark_payment_success,
    payment_status_payload,
)
from payment.zarinpal_client import ZarinPalRequestFailed

from order.forms import CardToCardReceiptForm, CheckOutForm, OrderTrackingForm
from order.models import OrderModel
from order.permissions import HasCustomerAccessPermission
from order.pricing import get_checkout_pricing_context
from order.repositories import order_repo
from order.services import CouponValidationError, checkout_service, coupon_service

logger = logging.getLogger(__name__)


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
        context.update(
            checkout_service.get_checkout_page_context(user=self.request.user)
        )
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
            "payment", "card_receipt"
        )

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        pay = order.payment
        if pay is None or pay.method != PaymentMethodType.card_to_card.value:
            raise Http404()
        if pay.status != PaymentStatusType.awaiting_payment.value:
            raise Http404()
        return order

    def get_receipt(self):
        return getattr(self.object, "card_receipt", None)

    def get_form(self):
        kwargs = {"instance": self.get_receipt()}
        if self.request.method == "POST":
            kwargs["data"] = self.request.POST
            kwargs["files"] = self.request.FILES
        return CardToCardReceiptForm(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cfg = CardToCardSettings.get_solo()
        context["card_bank_name"] = cfg.bank_name
        context["card_holder"] = cfg.account_holder
        context["card_number"] = cfg.card_number
        context["card_iban"] = cfg.iban
        context["card_note"] = cfg.note
        context["receipt_social_links"] = cfg.get_receipt_social_links()
        context["receipt"] = self.get_receipt()
        if "form" not in context:
            context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        receipt = form.save(commit=False)
        is_new = receipt.pk is None
        receipt.order = self.object
        receipt.amount = self.object.get_price()
        if is_new or not receipt.transfer_datetime:
            receipt.transfer_datetime = timezone.now()
        receipt.save()
        return redirect(
            reverse("order:card-receipt-confirmation", kwargs={"pk": self.object.pk})
        )


class CardReceiptConfirmationView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    """صفحه تأیید پس از ارسال رسید کارت به کارت."""

    model = OrderModel
    template_name = "order/card-receipt-confirmation.html"
    context_object_name = "order"

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user).select_related(
            "payment", "card_receipt"
        )

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        pay = order.payment
        if pay is None or pay.method != PaymentMethodType.card_to_card.value:
            raise Http404()
        if not getattr(order, "card_receipt", None):
            raise Http404()
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["receipt"] = self.object.card_receipt
        return context


class BalePaymentInstructionsView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    """صفحهٔ دیپ‌لینک پرداخت با کیف‌پول بله."""

    model = OrderModel
    template_name = "order/bale-payment-instructions.html"
    context_object_name = "order"

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user).select_related(
            "payment"
        )

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        pay = order.payment
        if pay is None or pay.method != PaymentMethodType.bale.value:
            raise Http404()
        return order

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        pay = self.object.payment
        if pay.status in {
            PaymentStatusType.preparing.value,
            PaymentStatusType.shipped.value,
        }:
            return redirect(reverse("order:completed"))
        if pay.status in {
            PaymentStatusType.payment_failed.value,
            PaymentStatusType.cancelled.value,
        }:
            return redirect(reverse("order:failed"))
        return self.render_to_response(self.get_context_data(object=self.object))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay = self.object.payment
        client = BaleClient()
        deep_link = client.build_deep_link(pay.link_token) if pay.link_token else ""
        from payment.bale_config import get_bale_config

        context["deep_link"] = deep_link
        context["bot_username"] = get_bale_config().bot_username
        context["link_expired"] = not pay.is_link_token_valid()
        context["status_url"] = reverse(
            "order:bale-payment-status", kwargs={"pk": self.object.pk}
        )
        context["inquire_url"] = reverse(
            "order:bale-payment-inquire", kwargs={"pk": self.object.pk}
        )
        return context


class BalePaymentStatusView(LoginRequiredMixin, HasCustomerAccessPermission, View):
    """JSON polling endpoint for Bale payment status."""

    def get(self, request, *args, **kwargs):
        order = (
            OrderModel.objects.filter(pk=kwargs["pk"], user=request.user)
            .select_related("payment")
            .first()
        )
        if (
            order is None
            or order.payment is None
            or order.payment.method != PaymentMethodType.bale.value
        ):
            raise Http404()
        return JsonResponse(payment_status_payload(order.payment, order))


class BalePaymentInquireView(LoginRequiredMixin, HasCustomerAccessPermission, View):
    """Recovery: inquireTransaction then finalize if paid."""

    def post(self, request, *args, **kwargs):
        order = (
            OrderModel.objects.filter(pk=kwargs["pk"], user=request.user)
            .select_related("payment")
            .first()
        )
        if (
            order is None
            or order.payment is None
            or order.payment.method != PaymentMethodType.bale.value
        ):
            raise Http404()

        payment = order.payment
        if payment.status in {
            PaymentStatusType.preparing.value,
            PaymentStatusType.shipped.value,
        }:
            return JsonResponse(payment_status_payload(payment, order))

        tx_id = payment.bale_telegram_payment_charge_id or payment.bale_pre_checkout_id
        if not tx_id:
            return JsonResponse(
                {
                    **payment_status_payload(payment, order),
                    "inquire": "no_transaction_id",
                }
            )

        client = BaleClient()
        try:
            tx = client.inquire_transaction(tx_id)
        except BaleAPIError as exc:
            # Network/API errors must not mark the payment failed.
            logger.warning("Bale inquireTransaction failed: %s", exc)
            return JsonResponse(
                {
                    **payment_status_payload(payment, order),
                    "inquire": "error",
                    "error": str(exc),
                }
            )

        if inquire_transaction_matches_payment(tx or {}, payment):
            charge = (
                (tx or {}).get("id") or payment.bale_telegram_payment_charge_id or tx_id
            )
            mark_payment_success(
                payment,
                response_json={"inquireTransaction": tx},
                bale_telegram_payment_charge_id=str(charge),
            )
            payment.refresh_from_db()
            order.refresh_from_db()
            request.session["last_order_tracking_code"] = order.tracking_code
            inquire_status = "paid"
        else:
            inquire_status = (
                (tx or {}).get("status") or (tx or {}).get("Status") or "mismatch"
            )

        payload = payment_status_payload(payment, order)
        payload["inquire"] = inquire_status
        return JsonResponse(payload)


class ValidateCouponView(LoginRequiredMixin, HasCustomerAccessPermission, View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get("code")
        user = request.user

        try:
            coupon = coupon_service.get_valid_coupon(code=code, user=user)
        except CouponValidationError as exc:
            response = HttpResponse(status=exc.status_code)
            response["HX-Trigger"] = json.dumps(
                {
                    "showToast": {
                        "text": exc.message,
                        "className": "error",
                        "background": "red",
                        "duration": 3000,
                    }
                }
            )
            return response

        cart = CartModel.objects.get(user=user)
        pricing_ctx = get_checkout_pricing_context(
            cart.calculate_total_price(),
            city=(request.POST.get("city") or "").strip(),
            state=(request.POST.get("state") or "").strip(),
            coupon_percent=coupon.discount_percent,
        )
        response = render(
            request,
            "order/partials/checkout-pricing-fragment.html",
            {
                **pricing_ctx,
                "coupon_percent": coupon.discount_percent,
            },
        )
        response["HX-Trigger"] = json.dumps(
            {
                "showToast": {
                    "text": "کد تخفیف با موفقیت ثبت شد",
                    "className": "info",
                    "background": "blue",
                    "duration": 2500,
                }
            }
        )
        return response

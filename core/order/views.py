import uuid

from django.contrib import messages
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, FormView, TemplateView, View

from cart.cart import CartSession
from cart.models import CartModel, CartItemModel
from order.forms import CheckOutForm, OrderTrackingForm
from order.models import CouponModel, OrderItemModel, OrderModel, UserAddressModel
from order.permissions import HasCustomerAccessPermission
from payment.models import (
    CardToCardSettings,
    PaymentMethodType,
    PaymentModel,
    PaymentStatusType,
)
from payment.zarinpal_client import ZarinPalRequestFailed, ZarinPalSandbox


class OrderCheckOutView(LoginRequiredMixin, HasCustomerAccessPermission, FormView):
    template_name = "order/checkout.html"
    form_class = CheckOutForm
    success_url = reverse_lazy('order:completed')

    def get_form_kwargs(self):
        kwargs = super(OrderCheckOutView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        cleaned_data = form.cleaned_data
        address = cleaned_data["address_id"]
        coupon = cleaned_data["coupon"]

        cart = CartModel.objects.get(user=user)
        payment_method = cleaned_data["payment_method"]
        try:
            with transaction.atomic():
                order = self.create_order(address)
                self.create_order_items(order, cart)
                total_price = order.calculate_total_price()
                self.apply_coupon(coupon, order, user, total_price)
                order.save()
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
        return reverse_lazy(
            "order:card-payment-instructions", kwargs={"pk": order.pk}
        )

    def create_order(self, address):
        return OrderModel.objects.create(
            user=self.request.user,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
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

    def apply_coupon(self, coupon, order, user, total_price):
        if coupon:
            # discount_amount = round(
            #     (total_price * Decimal(coupon.discount_percent / 100)))
            # total_price -= discount_amount

            order.coupon = coupon
            coupon.used_by.add(user)
            coupon.save()

        order.total_price = total_price

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartModel.objects.get(user=self.request.user)
        context["addresses"] = UserAddressModel.objects.filter(
            user=self.request.user)
        total_price = cart.calculate_total_price()
        context["total_price"] = total_price
        context["total_tax"] = round((total_price * 9)/100)
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
                return self.render_to_response(
                    self.get_context_data(form=form)
                )
            form = self.form_class(initial={"tracking_code": code})
            return self.render_to_response(
                self.get_context_data(form=form)
            )
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
        return context


class ValidateCouponView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, request, *args, **kwargs):
        code = request.POST.get("code")
        user = self.request.user

        status_code = 200
        message = "کد تخفیف با موفقیت ثبت شد"
        total_price = 0
        total_tax = 0

        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            return JsonResponse({"message": "کد تخفیف یافت نشد"}, status=404)
        else:
            if coupon.used_by.count() >= coupon.max_limit_usage:
                status_code, message = 403, "محدودیت در تعداد استفاده"

            elif coupon.expiration_date and coupon.expiration_date < timezone.now():
                status_code, message = 403, "کد تخفیف منقضی شده است"

            elif user in coupon.used_by.all():
                status_code, message = 403, "این کد تخفیف قبلا توسط شما استفاده شده است"

            else:
                cart = CartModel.objects.get(user=self.request.user)

                total_price = cart.calculate_total_price()
                total_price = round(
                    total_price - (total_price * (coupon.discount_percent/100)))
                total_tax = round((total_price * 9)/100)
        return JsonResponse({"message": message, "total_tax": total_tax, "total_price": total_price}, status=status_code)
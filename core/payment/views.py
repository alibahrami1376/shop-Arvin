from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View

from order.models import OrderModel, OrderStatusType
from order.permissions import HasCustomerAccessPermission
from .models import PaymentMethodType, PaymentModel, PaymentStatusType
from .zarinpal_client import ZarinPalSandbox

# Create your views here.


class PaymentVerifyView(LoginRequiredMixin, HasCustomerAccessPermission, View):
    def get(self, request, *args, **kwargs):
        authority_id = (request.GET.get("Authority") or "").strip()
        if not authority_id:
            return HttpResponseBadRequest()

        payment_obj = get_object_or_404(
            PaymentModel,
            authority_id=authority_id,
            method=PaymentMethodType.gateway.value,
        )
        order = get_object_or_404(
            OrderModel,
            payment=payment_obj,
            user=request.user,
        )
        zarin_pal = ZarinPalSandbox()
        response = zarin_pal.payment_verify(
            int(payment_obj.amount), payment_obj.authority_id
        )
        status_code = response.get("Status")
        ref_id = response.get("RefID")

        payment_obj.ref_id = ref_id
        payment_obj.response_code = status_code
        payment_obj.status = (
            PaymentStatusType.preparing.value
            if status_code in {100, 101}
            else PaymentStatusType.payment_failed.value
        )
        payment_obj.response_json = response
        payment_obj.save()

        order.status = (
            OrderStatusType.success.value
            if status_code in {100, 101}
            else OrderStatusType.failed.value
        )
        order.save()

        return redirect(
            reverse_lazy("order:completed")
            if status_code in {100, 101}
            else reverse_lazy("order:failed")
        )

import json
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from order.models import OrderModel
from order.permissions import HasCustomerAccessPermission

from .bale_webhook import handle_update
from .models import PaymentMethodType, PaymentModel
from .services import mark_payment_failed, mark_payment_success
from .zarinpal_client import ZarinPalSandbox

logger = logging.getLogger(__name__)


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
        success = status_code in {100, 101}

        if success:
            mark_payment_success(
                payment_obj,
                response_json=response,
                response_code=status_code,
                ref_id=ref_id,
            )
        else:
            mark_payment_failed(
                payment_obj,
                response_json=response,
                response_code=status_code,
            )

        request.session["last_order_tracking_code"] = order.tracking_code

        return redirect(
            reverse_lazy("order:completed") if success else reverse_lazy("order:failed")
        )


@method_decorator(csrf_exempt, name="dispatch")
class BaleBotWebhookView(View):
    """Receive Bale Bot API updates (must be HTTPS publicly)."""

    def post(self, request, *args, **kwargs):
        import hmac

        secret = (getattr(settings, "BALE_WEBHOOK_SECRET", "") or "").strip()
        if not secret:
            logger.error("BALE_WEBHOOK_SECRET is not configured; rejecting webhook")
            return HttpResponseForbidden("webhook secret not configured")

        provided = (
            request.headers.get("X-Bale-Webhook-Secret")
            or request.GET.get("secret")
            or ""
        )
        if not hmac.compare_digest(provided, secret):
            return HttpResponseForbidden("invalid webhook secret")

        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            return HttpResponseBadRequest("invalid json")

        try:
            handle_update(payload)
        except Exception:
            logger.exception("Bale webhook handler error")
            # Always 200 to avoid endless retries for logic bugs; log for ops.
        return HttpResponse("ok")

    def get(self, request, *args, **kwargs):
        return HttpResponse("bale webhook")

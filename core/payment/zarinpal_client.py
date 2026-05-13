import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ZarinPalRequestFailed(Exception):
    """درخواست پرداخت توسط زرین‌پال رد شد یا پاسخ نامعتبر بود."""


def get_domain():
    try:
        from django.contrib.sites.models import Site

        return Site.objects.get_current().domain
    except Exception:
        return "example.com"


def get_protocol():
    return "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http"


def _http_json_or_errors(response):
    """Parse JSON body; never raises JSONDecodeError."""
    text = (getattr(response, "text", None) or "") or ""
    stripped = text.strip()
    if not stripped:
        return None, f"پاسخ خالی از درگاه (کد HTTP {response.status_code})"
    try:
        return json.loads(stripped), None
    except json.JSONDecodeError:
        snippet = stripped[:400].replace("\n", " ")
        logger.warning(
            "ZarinPal non-JSON response: status=%s body=%s",
            response.status_code,
            snippet,
        )
        return None, (
            f"پاسخ غیر JSON از درگاه (کد HTTP {response.status_code}). "
            "MerchantID، آدرس Callback (دامنهٔ سایت) یا اتصال شبکه را بررسی کنید."
        )


class ZarinPalSandbox:
    _payment_request_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    _payment_verify_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
    _payment_page_url = "https://sandbox.zarinpal.com/pg/StartPay/"
    _callback_url = f"{get_protocol()}://{get_domain()}/payment/verify"

    def __init__(self, merchant_id=settings.MERCHANT_ID):
        self.merchant_id = merchant_id

    def payment_request(self, amount, description="پرداختی کاربر"):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": str(amount),
            "CallbackURL": self._callback_url,
            "Description": description,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self._payment_request_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=(5, 45),
            )
        except requests.RequestException as exc:
            logger.exception("ZarinPal payment_request network error")
            raise ZarinPalRequestFailed(
                "اتصال به درگاه پرداخت برقرار نشد. اینترنت یا فایروال را بررسی کنید."
            ) from exc

        data, err = _http_json_or_errors(response)
        if err:
            raise ZarinPalRequestFailed(err)

        status = data.get("Status")
        authority = (data.get("Authority") or "").strip()
        ok = bool(authority) and (status == 100 or status == "100")
        if not ok:
            errors = data.get("Errors") or data.get("errors")
            if isinstance(errors, list) and errors:
                msg = " ".join(str(x) for x in errors)
            else:
                msg = f"Status={status!r}"
            raise ZarinPalRequestFailed(f"درگاه پرداخت درخواست را رد کرد ({msg}).")

        return data

    def payment_verify(self, amount, authority):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": amount,
            "Authority": authority,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self._payment_verify_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=(5, 45),
            )
        except requests.RequestException as exc:
            logger.exception("ZarinPal payment_verify network error")
            return {
                "Status": -1,
                "RefID": None,
                "Errors": [str(exc)],
            }

        data, err = _http_json_or_errors(response)
        if err:
            return {"Status": -1, "RefID": None, "Errors": [err]}
        return data

    def generate_payment_url(self, authority):
        return f"{self._payment_page_url}{authority}"

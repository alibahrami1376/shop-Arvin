import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# کدهای خطای API مدیانا (فقط این‌ها = شکست ارسال)
MEDIANA_ERROR_MESSAGES = {
    1021: "خطای ناشناخته‌ای رخ داده است.",
    1032: "برنامه فعالی یافت نشد.",
    1033: "برنامه دارای قابلیت API نیست.",
    1034: "برنامه دارای قابلیت الگو نیست.",
    1035: "برنامه دارای قابلیت خط اختصاصی نیست.",
    1041: "دریافت‌کننده نامعتبر در درخواست API.",
    1042: "موجودی کیف پول کافی نیست.",
    1043: "حداکثر تعداد دریافت‌کنندگان تجاوز شده است.",
    1044: "شناسه پیامک نامعتبر است.",
    1045: "کد درخواست نامعتبر است.",
    1046: "پارامترهای ورودی نامعتبر هستند.",
    1047: "شماره تلفن در لیست سیاه قرار دارد.",
    1048: "WebEngage فعال نشده است.",
    1051: "کمپین منقضی شده است.",
    1061: "خط فعالی یافت نشد.",
    1062: "خط در این زمان از روز قابل استفاده نیست.",
    1071: "URL الگو شناسایی شد.",
    1072: "الگو توسط مدیر رد شد.",
    1073: "الگو متعلق به شماره ارسال دیگری است.",
    1074: "متن پیام خالی است.",
    1075: "درخواست پیام یافت نشد.",
    1076: "الگو خالی است.",
    1081: "کد پستی تایید نشده است.",
    1082: "کد ملی تایید نشده است.",
    1083: "شماره موبایل تایید نشده است.",
    1084: "پروفایل کامل نشده است.",
    1093: "دریافت‌کنندگان یافت نشدند.",
    1101: "شماره ارسال یافت نشد.",
    1102: "شماره ارسال منقضی شده است.",
}

# وضعیت تحویل پیامک مدیانا (فقط برای نمایش/لاگ؛ نشانه شکست ارسال نیست)
MEDIANA_STATUS_MESSAGES = {
    -3: "لیست سیاه",
    -2: "لیست سیاه",
    -1: "تکراری",
    0: "نامشخص",
    1: "در صف ارسال",
    2: "در حال ارسال",
    4: "ارسال شده",
    5: "رسیده به گوشی",
    6: "لغو شده",
    7: "نرسیده به گوشی",
    8: "لیست سیاه",
    9: "رسیده به مخابرات",
}


def mediana_error_message(code) -> str | None:
    try:
        return MEDIANA_ERROR_MESSAGES.get(int(code))
    except (TypeError, ValueError):
        return None


def mediana_status_message(code) -> str | None:
    try:
        return MEDIANA_STATUS_MESSAGES.get(int(code))
    except (TypeError, ValueError):
        return None


class MedianaSMS:
    """ارسال پیامک از طریق API مدیانا."""

    def __init__(self):
        self.base_url = (getattr(settings, "BASE_URL_MEDIANA", "") or "").rstrip("/")
        self.api_key = getattr(settings, "MEDIANA_API_KEY", "") or ""
        self.otp_pattern = getattr(settings, "MEDIANA_OTP_PATTERN_CODE", "") or ""
        self.order_pattern = getattr(settings, "MEDIANA_ORDER_PATTERN_CODE", "") or ""

    @property
    def url_send_otp(self) -> str:
        return f"{self.base_url}/sms/v1/send/otp"

    def send_otp(self, phone_number: str, otp_code: str) -> tuple[bool, str | None]:
        """
        ارسال کد OTP با الگوی مدیانا.
        برمی‌گرداند: (موفق؟, پیام خطا در صورت شکست)
        """
        if not self.api_key:
            logger.error("MEDIANA_API_KEY در تنظیمات خالی است.")
            return False, "کلید API مدیانا تنظیم نشده است."
        if not self.base_url:
            logger.error("BASE_URL_MEDIANA در تنظیمات خالی است.")
            return False, "آدرس سرویس مدیانا تنظیم نشده است."
        if not self.otp_pattern:
            logger.error("MEDIANA_OTP_PATTERN_CODE در تنظیمات خالی است.")
            return False, "کد الگوی OTP مدیانا تنظیم نشده است."

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            "patternCode": self.otp_pattern,
            "recipient": phone_number,
            "otpCode": str(otp_code),
        }

        try:
            response = requests.post(
                self.url_send_otp,
                json=data,
                headers=headers,
                timeout=10,
            )
        except requests.RequestException as exc:
            logger.exception("خطای ارتباط با مدیانا: %s", exc)
            return False, "خطای ارتباط با سرویس پیامک."

        payload = self._safe_json(response)
        if response.status_code >= 400:
            detail = self._extract_error_message(payload) or "ارسال پیامک با خطا مواجه شد."
            logger.error(
                "خطای API مدیانا (%s): %s — body=%s",
                response.status_code,
                detail,
                response.text[:500],
            )
            return False, detail

        # فقط کدهای خطای شناخته‌شده مدیانا = شکست؛ status تحویل (۰ و …) شکست نیست
        business_error = self._extract_known_error_code(payload)
        if business_error:
            logger.error(
                "خطای کسب‌وکاری مدیانا: %s — body=%s",
                business_error,
                response.text[:500],
            )
            return False, business_error

        logger.info(
            "پیامک OTP مدیانا برای %s ارسال شد. پاسخ: %s",
            phone_number,
            response.text[:500],
        )
        return True, None

    @staticmethod
    def _safe_json(response: requests.Response):
        try:
            return response.json()
        except ValueError:
            return None

    @classmethod
    def _extract_known_error_code(cls, payload) -> str | None:
        """فقط اگر کد خطا در جدول MEDIANA_ERROR_MESSAGES باشد."""
        if not isinstance(payload, dict):
            return None

        for candidate in cls._iter_dicts(payload):
            for key in (
                "code",
                "errorCode",
                "error_code",
                "messageCode",
                "message_code",
            ):
                if key not in candidate:
                    continue
                mapped = mediana_error_message(candidate.get(key))
                if mapped:
                    return mapped
        return None

    @classmethod
    def _extract_error_message(cls, payload) -> str | None:
        """برای پاسخ‌های HTTP خطا: کد شناخته‌شده یا پیام متنی."""
        known = cls._extract_known_error_code(payload)
        if known:
            return known
        if not isinstance(payload, dict):
            return None
        for candidate in cls._iter_dicts(payload):
            for key in ("message", "detail", "error", "msg", "title"):
                value = candidate.get(key)
                if value and not isinstance(value, (dict, list)):
                    return str(value)
        return None

    @staticmethod
    def _iter_dicts(payload: dict):
        yield payload
        for key in ("meta", "data", "error", "errors", "result"):
            nested = payload.get(key)
            if isinstance(nested, dict):
                yield nested

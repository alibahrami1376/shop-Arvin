import logging
import random
import re

from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# پیام‌های شناخته‌شده کاوه‌نگار (verify_lookup)
KAVENEGAR_ERROR_MESSAGES = {
    426: (
        "این الگو نیازمند سرویس پیشرفته (Lookup) در پنل کاوه‌نگار است. "
        "پلن را ارتقا دهید یا الگوی ساده‌تر بسازید."
    ),
    431: (
        "متغیرهای الگو (token) با تعریف پنل کاوه‌نگار همخوان نیست. "
        "کد OTP باید ۶ رقم باشد؛ token2 (مدت اعتبار) فقط عدد لاتین باشد."
    ),
    501: (
        "در حالت آزمایشی کاوه‌نگار فقط به شماره موبایل ثبت‌شده در همان حساب پیامک ارسال می‌شود."
    ),
    418: "اعتبار پیامک کافی نیست.",
    421: "پذیرنده (خط) نامعتبر است.",
}


def sms_otp_enabled() -> bool:
    from accounts.models import SMSSettings

    return SMSSettings.get_solo().sms_enabled


def get_valid_otp(mobile: str, code: str):
    """آخرین OTP معتبر برای موبایل را برمی‌گرداند یا ValidationError."""
    from accounts.models import OTPCode

    otp = (
        OTPCode.objects.filter(mobile=mobile, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if not otp or not otp.is_valid():
        raise ValidationError(
            "کد نامعتبر یا منقضی شده است. دوباره درخواست دهید.",
            code="invalid_otp",
        )
    if otp.code != str(code).strip():
        raise ValidationError("کد وارد شده اشتباه است.", code="wrong_otp")
    return otp


def consume_otp(otp) -> None:
    otp.is_used = True
    otp.save(update_fields=["is_used"])


def generate_otp_code():
    """تولید کد ۶ رقمی عددی تصادفی."""
    return str(random.randint(100000, 999999))


def _normalize_otp_token(code: str) -> str:
    """کد OTP فقط ارقام لاتین ۶ رقمی (مطابق محدودیت‌های کاوه‌نگار)."""
    persian = "۰۱۲۳۴۵۶۷۸۹"
    latin = "0123456789"
    digits = str(code).strip().translate(str.maketrans(persian, latin))
    digits = "".join(ch for ch in digits if ch.isdigit())
    if len(digits) != 6:
        raise ValueError("کد OTP باید دقیقاً ۶ رقم باشد.")
    return digits


def _sanitize_lookup_token(value: str, max_length: int = 20, *, fallback: str = "0") -> str:
    """
    token2 در Lookup کاوه‌نگار: معمولاً فقط رقم (نوع عددی در پنل).
    «۲ دقیقه» یا «-» خطای 431 می‌دهد؛ متن «دقیقه» را در الگوی پنل بنویسید، نه در token2.
    """
    if not value:
        return fallback
    s = str(value).strip()
    persian = "۰۱۲۳۴۵۶۷۸۹"
    latin = "0123456789"
    s = s.translate(str.maketrans(persian, latin))
    digits = "".join(ch for ch in s if ch.isdigit())
    if not digits:
        return fallback
    return digits[:max_length]


def _parse_kavenegar_api_exception(exc) -> str:
    raw = ""
    if exc.args:
        arg0 = exc.args[0]
        raw = arg0.decode("utf-8", errors="replace") if isinstance(arg0, bytes) else str(arg0)
    else:
        raw = str(exc)

    match = re.search(r"APIException\[(\d+)\]", raw)
    if match:
        code = int(match.group(1))
        if code in KAVENEGAR_ERROR_MESSAGES:
            return KAVENEGAR_ERROR_MESSAGES[code]

    if "message" in raw or len(raw) > 20:
        parts = raw.split("]", 1)
        if len(parts) > 1:
            return parts[1].strip() or "خطای ارسال پیامک از سمت کاوه‌نگار."
    return "ارسال پیامک با خطا مواجه شد. تنظیمات الگو و پنل کاوه‌نگار را بررسی کنید."


def send_otp_via_kavenegar(phone_number: str, code: str) -> tuple[bool, str | None]:
    """
    ارسال OTP با verify_lookup.
    برمی‌گرداند: (موفق؟, پیام خطا در صورت شکست)
    """
    from accounts.models import SMSSettings

    if not SMSSettings.get_solo().sms_enabled:
        logger.warning(
            "ارسال OTP به %s انجام نشد: ارسال پیامک در تنظیمات ادمین غیرفعال است.",
            phone_number,
        )
        return False, "ارسال پیامک در تنظیمات سایت غیرفعال است."

    api_key = getattr(settings, "KAVENEGAR_API_KEY", "") or ""
    template = getattr(settings, "KAVENEGAR_TEMPLATE", "verify")
    if not api_key:
        logger.error("KAVENEGAR_API_KEY در تنظیمات خالی است.")
        return False, "کلید API کاوه‌نگار تنظیم نشده است."

    try:
        token = _normalize_otp_token(code)
    except ValueError as exc:
        return False, str(exc)

    try:
        from kavenegar import APIException, HTTPException, KavenegarAPI
    except ImportError as exc:
        logger.exception("پکیج kavenegar نصب نیست: %s", exc)
        return False, "سرویس پیامک در سرور پیکربندی نشده است."

    from accounts.models import OTPCode

    token2 = _sanitize_lookup_token(
        str(OTPCode.VALIDITY_MINUTES),
        fallback=str(OTPCode.VALIDITY_MINUTES),
    )

    params = {
        "receptor": phone_number,
        "template": template,
        "token": token,
        "token2": token2,
        "type": "sms",
    }

    try:
        api = KavenegarAPI(api_key)
        response = api.verify_lookup(params)
        logger.info("پیامک OTP برای %s ارسال شد. پاسخ: %s", phone_number, response)
        return True, None
    except APIException as exc:
        detail = _parse_kavenegar_api_exception(exc)
        logger.error("خطای API کاوه‌نگار (verify_lookup): %s — %s", exc, detail)
        return False, detail
    except HTTPException as exc:
        logger.exception("خطای HTTP کاوه‌نگار: %s", exc)
        return False, "خطای ارتباط با سرور کاوه‌نگار."
    except Exception as exc:
        logger.exception("خطای غیرمنتظره هنگام ارسال OTP: %s", exc)
        return False, "ارسال پیامک با خطای داخلی مواجه شد."

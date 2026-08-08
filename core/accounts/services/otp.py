from django.core.exceptions import ValidationError

from accounts.models import OTPCode
from accounts.services.sms import MedianaSMS


class OTPService:
    """ساخت، ارسال و تأیید کد OTP ثبت‌نام موبایل."""

    def __init__(self, sms_client: MedianaSMS | None = None):
        self.sms = sms_client or MedianaSMS()

    def create_and_send(
        self,
        phone_number: str,
        user=None,
    ) -> tuple[OTPCode | None, str | None]:
        """
        OTP می‌سازد و با مدیانا می‌فرستد.
        برمی‌گرداند: (otp, پیام خطا)
        """
        otp = OTPCode(mobile=phone_number, user=user)
        otp.save()
        ok, err = self.sms.send_otp(phone_number=phone_number, otp_code=otp.code)
        if not ok:
            otp.delete()
            return None, err or "ارسال پیامک با خطا مواجه شد."
        return otp, None

    def get_valid(self, phone_number: str, code: str) -> OTPCode:
        persian = "۰۱۲۳۴۵۶۷۸۹"
        latin = "0123456789"
        normalized_code = (
            str(code)
            .strip()
            .translate(str.maketrans(persian, latin))
        )
        normalized_code = "".join(ch for ch in normalized_code if ch.isdigit())

        otp = (
            OTPCode.objects.filter(mobile=phone_number, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if not otp or not otp.is_valid():
            raise ValidationError(
                "کد نامعتبر یا منقضی شده است. دوباره درخواست دهید.",
                code="invalid_otp",
            )
        if otp.code != normalized_code:
            raise ValidationError("کد وارد شده اشتباه است.", code="wrong_otp")
        return otp

    def consume(self, otp: OTPCode, user=None) -> None:
        otp.is_used = True
        update_fields = ["is_used"]
        if user is not None and otp.user_id != user.pk:
            otp.user = user
            update_fields.append("user")
        otp.save(update_fields=update_fields)

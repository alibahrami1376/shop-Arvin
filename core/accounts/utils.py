"""توابع کمکی احراز هویت — برای سازگاری با فرم‌ها."""

from accounts.services.otp import OTPService

_otp_service = OTPService()


def get_valid_otp(mobile: str, code: str):
    return _otp_service.get_valid(mobile, code)


def consume_otp(otp, user=None) -> None:
    _otp_service.consume(otp, user=user)

import re

from django.core.exceptions import ValidationError


def validate_iranian_cellphone_number(value):
    """
    فقط شماره موبایل ایرانی معتبر: ۱۱ رقم، شروع با 09.
    """
    if value is None:
        raise ValidationError("شماره موبایل الزامی است.")
    s = str(value).strip().replace(" ", "")
    # ارقام فارسی به لاتین
    persian = "۰۱۲۳۴۵۶۷۸۹"
    latin = "0123456789"
    trans = str.maketrans(persian, latin)
    s = s.translate(trans)
    pattern = r"^09\d{9}$"
    if not re.match(pattern, s):
        raise ValidationError(
            "شماره موبایل باید ۱۱ رقم و به صورت 09xxxxxxxxx (فقط اپراتورهای ایرانی) باشد."
        )
    return s

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """
    احراز هویت با ایمیل یا شماره موبایل ایرانی + رمز عبور.
    ورودی «username» می‌تواند ایمیل نرمال‌شده یا شماره 09xxxxxxxxx باشد.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        username = str(username).strip()
        user = None
        if "@" in username:
            email = User.objects.normalize_email(username)
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                logger.debug("ورود: کاربری با این ایمیل یافت نشد.")
                return None
        else:
            # نرمال‌سازی ارقام فارسی
            persian = "۰۱۲۳۴۵۶۷۸۹"
            latin = "0123456789"
            phone = username.translate(str.maketrans(persian, latin))
            if not phone.startswith("0") and len(phone) == 10:
                phone = "0" + phone
            try:
                user = User.objects.get(phone_number=phone)
            except User.DoesNotExist:
                logger.debug("ورود: کاربری با این موبایل یافت نشد.")
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

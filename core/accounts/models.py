import random
import logging

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.validators import validate_iranian_cellphone_number

logger = logging.getLogger(__name__)


class UserType(models.IntegerChoices):
    customer = 1, _("customer")
    admin = 2, _("admin")
    superuser = 3, _("superuser")


class UserManager(BaseUserManager):
    """
    Customer: Registration via mobile number (+ OTP if enabled).
    Superuser/Admin: Creation via email (mobile number not required).
    """

    def normalize_phone(self, phone):
        if not phone:
            return None
        s = str(phone).strip().replace(" ", "")
        validate_iranian_cellphone_number(s)
        return s

    def create_customer(
        self,
        phone_number,
        password=None,
        email=None,
        *,
        otp_code=None,
        phone_verified=None,
        **extra_fields,
    ):
        """ثبت‌نام مشتری با شماره موبایل."""
        if not password:
            raise ValueError(_("رمز عبور الزامی است."))
        if not phone_number:
            raise ValueError(_("شماره موبایل الزامی است."))

        phone_number = self.normalize_phone(phone_number)
        email = self.normalize_email(email) if email else None
        if email == "":
            email = None

        if phone_verified is None:
            from accounts.utils import consume_otp, get_valid_otp, sms_otp_enabled

            if sms_otp_enabled():
                if not otp_code:
                    raise ValueError(
                        _("ثبت‌نام نیازمند کد تأیید پیامک است. ابتدا کد را دریافت و وارد کنید.")
                    )
                try:
                    otp = get_valid_otp(phone_number, otp_code)
                except ValidationError as exc:
                    raise ValueError(exc.message) from exc
                consume_otp(otp)
                phone_verified = True
            else:
                phone_verified = True

        extra_fields.setdefault("phone_verified", phone_verified)
        extra_fields.setdefault("type", UserType.customer.value)

        user = self.model(
            email=email,
            phone_number=phone_number,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """سوپریوزر با ایمیل؛ موبایل اختیاری و بدون OTP."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("phone_verified", True)
        extra_fields.setdefault("type", UserType.superuser.value)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if not email:
            raise ValueError(_("برای سوپریوزر، ایمیل الزامی است."))

        email = self.normalize_email(email)
        phone_number = extra_fields.pop("phone_number", None)
        if phone_number:
            phone_number = self.normalize_phone(phone_number)

        user = self.model(
            email=email,
            phone_number=phone_number,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Customer: Login and registration via mobile number.
    Superuser/Admin: Login via email (USERNAME_FIELD).
    """
    email = models.EmailField(
        _("ایمیل"),
        unique=True,
        null=True,
        blank=True,
        help_text=_("شناسه ورود ادمین و سوپریوزر"),
    )
    phone_number = models.CharField(
        _("شماره موبایل"),
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_iranian_cellphone_number],
        help_text=_("شناسه ورود و ثبت‌نام مشتری"),
    )
    phone_verified = models.BooleanField(_("موبایل تأیید شده"), default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(_("ایمیل تأیید شده"), default=False)
    type = models.IntegerField(
        choices=UserType.choices, default=UserType.customer.value
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربران")
        constraints = [
            models.CheckConstraint(
                check=Q(email__isnull=False) | Q(phone_number__isnull=False),
                name="accounts_user_email_or_phone_required",
            ),
        ]

    @property
    def is_staff_account(self):
        return self.is_superuser or self.is_staff

    def save(self, *args, **kwargs):
        if self.email == "":
            self.email = None
        elif self.email:
            self.email = User.objects.normalize_email(self.email)
        if self.phone_number == "":
            self.phone_number = None
        elif self.phone_number:
            self.phone_number = User.objects.normalize_phone(self.phone_number)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.is_staff_account:
            if not self.email:
                raise ValidationError({"email": _("برای ادمین، ایمیل الزامی است.")})
        elif not self.phone_number:
            raise ValidationError(
                {"phone_number": _("برای مشتری، شماره موبایل الزامی است.")}
            )

    def __str__(self):
        if self.email:
            return self.email
        if self.phone_number:
            return self.phone_number
        return f"User({self.pk})"


class Profile(models.Model):
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="user_profile",
    )
    first_name = models.CharField(_("نام"), max_length=255, blank=True)
    last_name = models.CharField(_("نام خانوادگی"), max_length=255, blank=True)
    image = models.ImageField(
        upload_to="profile/", default="profile/default.png", verbose_name=_("تصویر")
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("پروفایل")
        verbose_name_plural = _("پروفایل‌ها")

    def get_fullname(self):
        full = f"{self.first_name} {self.last_name}".strip()
        if full:
            return full
        if self.user.phone_number:
            return self.user.phone_number
        if self.user.email:
            return self.user.email
        return "کاربر جدید"


def ensure_user_profile(user):
    """پروفایل یک‌به‌یک کاربر را می‌سازد؛ در صورت sequence خراب PostgreSQL یک‌بار sequence را اصلاح می‌کند."""
    from django.db import IntegrityError

    from accounts.db_utils import reset_pg_id_sequences

    if Profile.objects.filter(user_id=user.pk).exists():
        return Profile.objects.get(user=user)
    try:
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile
    except IntegrityError:
        reset_pg_id_sequences(("accounts_profile",))
        try:
            return Profile.objects.create(user=user)
        except IntegrityError:
            return Profile.objects.get(user=user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """با ایجاد کاربر، پروفایل خالی ساخته می‌شود."""
    if created:
        ensure_user_profile(instance)


class OTPCode(models.Model):
    """کدهای یک‌بار مصرف برای ثبت‌نام / تأیید موبایل."""

    VALIDITY_MINUTES = 2

    mobile = models.CharField(_("موبایل"), max_length=11)
    code = models.CharField(_("کد"), max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(_("استفاده شده"), default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("کد OTP")
        verbose_name_plural = _("کدهای OTP")

    def save(self, *args, **kwargs):
        if not self.pk and not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def is_valid(self):
        """کد معتبر است اگر استفاده نشده و کمتر از VALIDITY_MINUTES دقیقه از ایجادش گذشته باشد."""
        if self.is_used:
            return False
        limit = self.created_at + timezone.timedelta(minutes=self.VALIDITY_MINUTES)
        return timezone.now() <= limit

    @classmethod
    def validity_seconds(cls):
        return cls.VALIDITY_MINUTES * 60

    def __str__(self):
        return f"{self.mobile} — {self.code}"


class SMSSettings(models.Model):
    """
    یک ردیف (singleton): فعال یا غیرفعال کردن ارسال پیامک OTP از پنل ادمین.
    وقتی فعال است، UserManager.create_customer بدون otp_code ثبت‌نام را نمی‌پذیرد.
    """

    sms_enabled = models.BooleanField(
        _("ارسال پیامک OTP فعال است"),
        default=True,
        help_text=_(
            "فعال: ثبت‌نام فقط پس از تأیید پیامک. "
            "غیرفعال: ثبت‌نام با موبایل بدون ارسال پیامک."
        ),
    )
    updated_date = models.DateTimeField(_("آخرین به‌روزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("تنظیمات پیامک (OTP)")
        verbose_name_plural = _("تنظیمات پیامک (OTP)")

    def __str__(self):
        return _("تنظیمات پیامک OTP")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

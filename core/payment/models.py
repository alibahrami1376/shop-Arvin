from django.db import models
from django.db.models import JSONField


class PaymentStatusType(models.IntegerChoices):
    awaiting_payment = 1, "در انتظار پرداخت"
    preparing = 2, "در حال آماده‌سازی"
    shipped = 3, "ارسال شده"
    payment_failed = 4, "پرداخت ناموفق"
    cancelled = 5, "لغو شده"


class PaymentMethodType(models.IntegerChoices):
    gateway = 1, "درگاه آنلاین"
    card_to_card = 2, "کارت به کارت"


class PaymentMethodSettings(models.Model):
    """تنظیم نمایش روش‌های پرداخت در سایت (یک ردیف)."""

    gateway_enabled = models.BooleanField(
        default=True,
        verbose_name="نمایش درگاه آنلاین (زرین‌پال)",
    )
    card_to_card_enabled = models.BooleanField(
        default=True,
        verbose_name="نمایش کارت به کارت",
    )
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات روش‌های پرداخت"
        verbose_name_plural = "تنظیمات روش‌های پرداخت"

    def __str__(self):
        return "تنظیمات روش‌های پرداخت"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def is_method_enabled(self, method):
        if method == PaymentMethodType.gateway.value:
            return self.gateway_enabled
        if method == PaymentMethodType.card_to_card.value:
            return self.card_to_card_enabled
        return False

    def get_enabled_methods(self):
        enabled = []
        if self.gateway_enabled:
            enabled.append(
                (PaymentMethodType.gateway.value, PaymentMethodType.gateway.label)
            )
        if self.card_to_card_enabled:
            enabled.append(
                (
                    PaymentMethodType.card_to_card.value,
                    PaymentMethodType.card_to_card.label,
                )
            )
        return enabled


class PaymentModel(models.Model):
    method = models.IntegerField(
        choices=PaymentMethodType.choices,
        default=PaymentMethodType.gateway.value,
        verbose_name="روش پرداخت",
    )
    authority_id = models.CharField(max_length=255)
    ref_id = models.BigIntegerField(null=True, blank=True)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    response_json = JSONField(default=dict)
    response_code = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(
        choices=PaymentStatusType.choices,
        default=PaymentStatusType.awaiting_payment.value,
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        label = PaymentMethodType(self.method).label
        return f"{label} — {self.authority_id[:24]}"


RECEIPT_SOCIAL_PLATFORMS = (
    ("telegram", "تلگرام", "bi-telegram"),
    ("bale", "بله", None),
    ("rubika", "روبیکا", None),
    ("whatsapp", "واتساپ", "bi-whatsapp"),
    ("email", "ایمیل", "bi-envelope"),
)


class CardToCardSettings(models.Model):
    """یک ردیف (singleton) برای نمایش به مشتری در صفحهٔ کارت به کارت."""

    bank_name = models.CharField(max_length=255, blank=True, verbose_name="نام بانک")
    account_holder = models.CharField(
        max_length=255, blank=True, verbose_name="نام صاحب حساب / کارت"
    )
    card_number = models.CharField(max_length=32, blank=True, verbose_name="شماره کارت")
    iban = models.CharField(max_length=34, blank=True, verbose_name="شبا (IBAN)")
    note = models.TextField(
        blank=True,
        verbose_name="متن راهنما برای مشتری",
        help_text="مثلاً درخواست ارسال فیش یا شماره سفارش.",
    )

    telegram_enabled = models.BooleanField(default=False, verbose_name="فعال — تلگرام")
    telegram_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک تلگرام",
        help_text="مثال: https://t.me/username",
    )
    bale_enabled = models.BooleanField(default=False, verbose_name="فعال — بله")
    bale_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک بله",
        help_text="مثال: https://ble.ir/username",
    )
    rubika_enabled = models.BooleanField(default=False, verbose_name="فعال — روبیکا")
    rubika_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک روبیکا",
    )
    whatsapp_enabled = models.BooleanField(default=False, verbose_name="فعال — واتساپ")
    whatsapp_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک واتساپ",
        help_text="لینک کامل یا شماره موبایل (مثال: 989121234567)",
    )
    email_enabled = models.BooleanField(default=False, verbose_name="فعال — ایمیل")
    email_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="ایمیل",
        help_text="آدرس ایمیل (مثال: shop@example.com)",
    )

    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات کارت به کارت"
        verbose_name_plural = "تنظیمات کارت به کارت"

    def __str__(self):
        return "تنظیمات کارت به کارت"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_receipt_social_links(self):
        links = []
        for key, label, icon in RECEIPT_SOCIAL_PLATFORMS:
            if not getattr(self, f"{key}_enabled", False):
                continue
            raw = (getattr(self, f"{key}_link", "") or "").strip()
            if not raw:
                continue
            url = self._normalize_receipt_link(key, raw)
            if url:
                links.append({"key": key, "label": label, "url": url, "icon": icon})
        return links

    @staticmethod
    def _normalize_receipt_link(platform, raw):
        if platform == "email":
            if raw.startswith("mailto:"):
                return raw
            return f"mailto:{raw}"
        if platform == "whatsapp":
            if raw.startswith("http://") or raw.startswith("https://"):
                return raw
            digits = "".join(c for c in raw if c.isdigit())
            if digits:
                return f"https://wa.me/{digits}"
            return ""
        return raw
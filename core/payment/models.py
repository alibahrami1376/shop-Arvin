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
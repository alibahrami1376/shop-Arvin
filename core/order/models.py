import secrets

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from order.shipping import ShippingMethodType

TRACKING_CODE_MIN_LENGTH = 5
TRACKING_CODE_MAX_LENGTH = 7


def generate_tracking_code():
    length = secrets.choice(
        range(TRACKING_CODE_MIN_LENGTH, TRACKING_CODE_MAX_LENGTH + 1)
    )
    first = secrets.choice("123456789")
    rest = "".join(secrets.choice("0123456789") for _ in range(length - 1))
    return first + rest


class OrderStatusType(models.IntegerChoices):
    pending = 1, "در انتظار پرداخت"
    success = 2, "موفقیت آمیز"
    failed = 3, "لغو شده"


class Province(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام استان")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "استان"
        verbose_name_plural = "استان‌ها"

    def __str__(self):
        return self.name


class City(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="cities",
        verbose_name="استان",
    )
    name = models.CharField(max_length=100, verbose_name="نام شهر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"
        unique_together = ("province", "name")

    def __str__(self):
        return f"{self.name} ({self.province.name})"


class UserAddressModel(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)

    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class CouponModel(models.Model):
    code = models.CharField(max_length=100)
    discount_percent = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_limit_usage = models.PositiveIntegerField(default=10)
    used_by = models.ManyToManyField(
        "accounts.User", related_name="coupon_users", blank=True
    )
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


# Create your models here.
class OrderModel(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT)

    tracking_code = models.CharField(
        max_length=7,
        unique=True,
        editable=False,
        verbose_name="کد سفارش",
    )

    shipping_method = models.IntegerField(
        choices=ShippingMethodType.choices,
        default=ShippingMethodType.address.value,
        verbose_name="روش ارسال",
    )

    freight_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="توضیحات باربری",
    )

    # order address information
    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    payment = models.ForeignKey(
        "payment.PaymentModel", on_delete=models.SET_NULL, null=True, blank=True
    )

    total_price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
        verbose_name="جمع کالاها",
        help_text="جمع قیمت اقلام قبل از تخفیف، ارسال و مالیات.",
    )
    discount_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
        verbose_name="مبلغ تخفیف",
    )
    shipping_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
        verbose_name="هزینه ارسال",
    )
    tax_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=0,
        verbose_name="مالیات",
    )

    coupon = models.ForeignKey(
        CouponModel, on_delete=models.PROTECT, null=True, blank=True
    )
    status = models.IntegerField(
        choices=OrderStatusType.choices, default=OrderStatusType.pending.value
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def calculate_total_price(self):
        return sum(item.price * item.quantity for item in self.order_items.all())

    def __str__(self):
        return f"{self.tracking_code} ({self.user.email})"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            for _ in range(32):
                code = generate_tracking_code()
                if not OrderModel.objects.filter(tracking_code=code).exists():
                    self.tracking_code = code
                    break
            else:
                raise RuntimeError("Could not generate a unique tracking code.")
        super().save(*args, **kwargs)

    def get_status(self):
        return {
            "id": self.status,
            "title": OrderStatusType(self.status).name,
            "label": OrderStatusType(self.status).label,
        }

    def get_customer_payment_status(self):
        """وضعیت پرداخت برای نمایش به مشتری (تأیید کارت‌به‌کارت یا موفقیت درگاه)."""
        from payment.models import PaymentMethodType, PaymentStatusType

        if self.payment is None:
            if self.status == OrderStatusType.success.value:
                label = "پرداخت موفق"
                variant = "success"
            elif self.status == OrderStatusType.failed.value:
                label = "پرداخت ناموفق"
                variant = "danger"
            else:
                label = OrderStatusType(self.status).label
                variant = "warning"
            return {"label": label, "variant": variant}

        payment_status = self.payment.status
        if payment_status == PaymentStatusType.awaiting_payment.value:
            if self.payment.method == PaymentMethodType.card_to_card.value:
                label = "در انتظار تأیید پرداخت"
            else:
                label = "در انتظار پرداخت"
            variant = "warning"
        elif payment_status in {
            PaymentStatusType.preparing.value,
            PaymentStatusType.shipped.value,
        }:
            label = "پرداخت موفق"
            variant = "success"
        elif payment_status == PaymentStatusType.payment_failed.value:
            label = "پرداخت ناموفق"
            variant = "danger"
        elif payment_status == PaymentStatusType.cancelled.value:
            label = "لغو شده"
            variant = "secondary"
        else:
            label = PaymentStatusType(payment_status).label
            variant = "secondary"
        return {"label": label, "variant": variant}

    def get_customer_order_status(self):
        """مرحلهٔ سفارش برای مشتری (همان وضعیتی که ادمین روی پرداخت تنظیم می‌کند)."""
        from payment.models import PaymentStatusType

        if self.payment is None:
            return {
                "label": OrderStatusType(self.status).label,
                "variant": "primary",
            }
        payment_status = self.payment.status
        variant = "primary"
        if payment_status == PaymentStatusType.awaiting_payment.value:
            variant = "warning"
        elif payment_status == PaymentStatusType.preparing.value:
            variant = "info"
        elif payment_status == PaymentStatusType.shipped.value:
            variant = "success"
        elif payment_status == PaymentStatusType.payment_failed.value:
            variant = "danger"
        elif payment_status == PaymentStatusType.cancelled.value:
            variant = "secondary"
        return {
            "label": PaymentStatusType(payment_status).label,
            "variant": variant,
        }

    def get_full_address(self):
        if self.shipping_method == ShippingMethodType.freight.value:
            parts = [ShippingMethodType.freight.label, self.city]
            if self.freight_notes:
                parts.append(self.freight_notes)
            return " — ".join(parts)
        return f"{self.state},{self.city},{self.address}"

    def get_shipping_method_label(self):
        return ShippingMethodType(self.shipping_method).label

    @property
    def is_successful(self):
        return self.status == OrderStatusType.success.value

    @property
    def can_customer_view_invoice(self):
        """فاکتور وقتی وضعیت پرداخت برای مشتری «موفق» است (تأیید ادمین یا درگاه)."""
        return self.get_customer_payment_status()["variant"] == "success"

    def get_items_subtotal(self) -> int:
        """جمع قیمت کالاها (ذخیره‌شده یا محاسبه از اقلام)."""
        if self.pk and self.order_items.exists():
            return int(self.calculate_total_price())
        return int(self.total_price)

    def get_discount_amount(self) -> int:
        if self.discount_amount:
            return int(self.discount_amount)
        if self.coupon:
            subtotal = self.get_items_subtotal()
            return round(subtotal * self.coupon.discount_percent / 100)
        return 0

    def get_shipping_amount(self) -> int:
        return int(self.shipping_amount or 0)

    def get_tax_amount(self) -> int:
        return int(self.tax_amount or 0)

    def get_price(self) -> int:
        """مبلغ قابل پرداخت (پس از تخفیف + ارسال + مالیات)."""
        base = self.get_items_subtotal() - self.get_discount_amount()
        return base + self.get_shipping_amount() + self.get_tax_amount()

    def get_pricing_breakdown(self) -> dict:
        """ردیف‌های نمایشی برای فاکتور و جزئیات سفارش."""
        settings = CheckoutPricingSettings.get_solo()
        items = self.get_items_subtotal()
        discount = self.get_discount_amount()
        return {
            "items_subtotal": items,
            "discount_amount": discount,
            "after_discount": items - discount,
            "shipping_amount": self.get_shipping_amount(),
            "tax_amount": self.get_tax_amount(),
            "grand_total": self.get_price(),
            "coupon": self.coupon,
            "shipping_enabled": settings.shipping_enabled,
            "tax_enabled": settings.tax_enabled,
            "tax_percent": settings.tax_percent,
        }


class OrderItemModel(models.Model):
    order = models.ForeignKey(
        OrderModel, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey("shop.ProductModel", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} - {self.order.tracking_code}"


class CheckoutPricingSettings(models.Model):
    """تنظیمات نمایش هزینه ارسال و مالیات در صفحه تسویه حساب (یک ردیف)."""

    shipping_enabled = models.BooleanField(
        default=True,
        verbose_name="نمایش هزینه ارسال",
        help_text="غیرفعال: بخش هزینه ارسال در خلاصه سفارش نمایش داده نمی‌شود.",
    )
    shipping_tehran_label = models.CharField(
        max_length=100,
        default="تهران و حومه",
        verbose_name="عنوان نرخ تهران",
    )
    shipping_tehran_amount = models.PositiveIntegerField(
        default=35000,
        verbose_name="هزینه ارسال تهران و حومه (تومان)",
    )
    shipping_province_label = models.CharField(
        max_length=100,
        default="شهرستان‌ها",
        verbose_name="عنوان نرخ شهرستان",
    )
    shipping_province_amount = models.PositiveIntegerField(
        default=50000,
        verbose_name="هزینه ارسال شهرستان‌ها (تومان)",
    )
    tax_enabled = models.BooleanField(
        default=True,
        verbose_name="نمایش و محاسبه مالیات",
        help_text="غیرفعال: مالیات در خلاصه سفارش محاسبه و نمایش داده نمی‌شود.",
    )
    tax_percent = models.PositiveSmallIntegerField(
        default=9,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="درصد مالیات",
    )
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات هزینه ارسال و مالیات"
        verbose_name_plural = "تنظیمات هزینه ارسال و مالیات"

    def __str__(self):
        return "تنظیمات هزینه ارسال و مالیات"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def calculate_tax_amount(self, subtotal) -> int:
        if not self.tax_enabled or self.tax_percent <= 0:
            return 0
        return round(subtotal * self.tax_percent / 100)

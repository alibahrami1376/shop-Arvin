import secrets

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

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
    pending = 1 , "در انتظار پرداخت"
    success = 2, "موفقیت آمیز"
    failed = 3,"لغو شده"

class UserAddressModel(models.Model):
    user = models.ForeignKey('accounts.User',on_delete=models.CASCADE)
    
    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class CouponModel(models.Model):
    code = models.CharField(max_length=100)
    discount_percent = models.IntegerField(default=0,validators = [MinValueValidator(0),MaxValueValidator(100)])
    max_limit_usage = models.PositiveIntegerField(default=10)
    used_by = models.ManyToManyField('accounts.User',related_name = "coupon_users",blank=True)
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField(null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


# Create your models here.
class OrderModel(models.Model):
    user = models.ForeignKey('accounts.User',on_delete=models.PROTECT)
    tracking_code = models.CharField(
        max_length=7,
        unique=True,
        editable=False,
        verbose_name="کد سفارش",
    )

    # order address information
    address = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    
    payment = models.ForeignKey('payment.PaymentModel',on_delete=models.SET_NULL,null=True,blank=True)
    
    
    total_price = models.DecimalField(default=0,max_digits=10,decimal_places=0)

    coupon = models.ForeignKey(CouponModel,on_delete=models.PROTECT,null=True,blank=True)
    status = models.IntegerField(choices=OrderStatusType.choices,default=OrderStatusType.pending.value)
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
            "id":self.status,
            "title":OrderStatusType(self.status).name,
            "label":OrderStatusType(self.status).label,
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
        return f"{self.state},{self.city},{self.address}"
    
    @property
    def is_successful(self):
        return self.status == OrderStatusType.success.value
    
    def get_price(self):
        
        if self.coupon:            
            return round(self.total_price - (self.total_price * Decimal( self.coupon.discount_percent /100)))
        else:
            return self.total_price
    
    
class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel,on_delete=models.CASCADE,related_name="order_items") 
    product = models.ForeignKey('shop.ProductModel',on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0,max_digits=10,decimal_places=0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.title} - {self.order.tracking_code}"
    
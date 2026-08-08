"""گزینه‌های ارسال در checkout."""

from django.db import models


class ShippingMethodType(models.IntegerChoices):
    address = 1, "ارسال به آدرس"
    freight = 2, "ارسال با باربری"


DELIVERY_ADDRESS = "address"
DELIVERY_FREIGHT = "freight"

DELIVERY_TYPE_CHOICES = [
    (DELIVERY_FREIGHT, "ارسال با باربری"),
]

FREIGHT_NOTES_PLACEHOLDER = (
    "مثلاً: نام باربری، شماره تماس گیرنده در مقصد، زمان تحویل یا سایر توضیحات"
)

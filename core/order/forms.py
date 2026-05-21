from django import forms
from django.utils import timezone
from payment.models import PaymentMethodSettings, PaymentMethodType

from order.models import CouponModel, UserAddressModel
from order.shipping import (
    DELIVERY_ADDRESS,
    DELIVERY_FREIGHT,
    DELIVERY_TYPE_CHOICES,
    FREIGHT_CITY_CHOICES,
    FREIGHT_NOTES_PLACEHOLDER,
)


class CheckOutForm(forms.Form):
    delivery_type = forms.ChoiceField(
        label="روش ارسال",
        choices=DELIVERY_TYPE_CHOICES,
        initial=DELIVERY_ADDRESS,
        widget=forms.RadioSelect,
        error_messages={"required": "روش ارسال را انتخاب کنید."},
    )
    address_id = forms.IntegerField(
        required=False,
        error_messages={"invalid": "آدرس انتخاب‌شده معتبر نیست."},
    )
    freight_city = forms.ChoiceField(
        label="شهر مقصد",
        choices=FREIGHT_CITY_CHOICES,
        required=False,
        error_messages={"invalid_choice": "شهر انتخاب‌شده معتبر نیست."},
    )
    freight_notes = forms.CharField(
        label="توضیحات باربری",
        required=False,
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": FREIGHT_NOTES_PLACEHOLDER,
            }
        ),
    )
    coupon = forms.CharField(required=False)
    payment_method = forms.TypedChoiceField(
        coerce=int,
        choices=[],
        error_messages={
            "required": "روش پرداخت را انتخاب کنید.",
            "invalid_choice": "روش پرداخت انتخاب‌شده معتبر نیست.",
        },
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        enabled = PaymentMethodSettings.get_solo().get_enabled_methods()
        self.fields["payment_method"].choices = enabled
        if enabled:
            self.fields["payment_method"].initial = enabled[0][0]
        else:
            self.fields["payment_method"].required = False

    def clean_address_id(self):
        address_id = self.cleaned_data.get("address_id")
        if not address_id:
            return None
        user = self.request.user
        try:
            return UserAddressModel.objects.get(id=address_id, user=user)
        except UserAddressModel.DoesNotExist:
            raise forms.ValidationError("آدرس انتخاب‌شده معتبر نیست.")

    def clean_freight_city(self):
        city = self.cleaned_data.get("freight_city")
        if city:
            return city
        return None

    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get("delivery_type")

        if delivery_type == DELIVERY_FREIGHT:
            if not cleaned_data.get("freight_city"):
                self.add_error("freight_city", "شهر مقصد را انتخاب کنید.")
            notes = (cleaned_data.get("freight_notes") or "").strip()
            if not notes:
                self.add_error(
                    "freight_notes",
                    "توضیحات باربری را برای هماهنگی ارسال وارد کنید.",
                )
            else:
                cleaned_data["freight_notes"] = notes
        elif delivery_type == DELIVERY_ADDRESS:
            if not cleaned_data.get("address_id"):
                self.add_error(
                    "address_id",
                    "یک آدرس را انتخاب کنید یا «ارسال با باربری» را برگزینید.",
                )

        return cleaned_data

    def clean_coupon(self):
        code = self.cleaned_data.get("coupon")
        if code == "":
            return None
        user = self.request.user
        coupon = None
        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            raise forms.ValidationError("کد تخفیف اشتباه است")
        if coupon:
            if coupon.used_by.count() >= coupon.max_limit_usage:
                raise forms.ValidationError("ظرفیت استفاده از این کد تخفیف تکمیل شده است.")

            if coupon.expiration_date and coupon.expiration_date < timezone.now():
                raise forms.ValidationError("کد تخفیف منقضی شده است")

            if user in coupon.used_by.all():
                raise forms.ValidationError("این کد تخفیف قبلا توسط شما استفاده شده است")

        return coupon

    def clean_payment_method(self):
        method = self.cleaned_data.get("payment_method")
        settings = PaymentMethodSettings.get_solo()
        enabled = settings.get_enabled_methods()
        if not enabled:
            raise forms.ValidationError("در حال حاضر هیچ روش پرداختی فعال نیست.")
        if method is None or not settings.is_method_enabled(method):
            raise forms.ValidationError("روش پرداخت انتخاب‌شده در دسترس نیست.")
        return method


class OrderTrackingForm(forms.Form):
    tracking_code = forms.CharField(
        label="کد سفارش",
        max_length=7,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "مثال: 123456",
                "autocomplete": "off",
                "dir": "ltr",
                "inputmode": "numeric",
                "pattern": "[0-9]{5,7}",
            }
        ),
    )

    def clean_tracking_code(self):
        code = self.cleaned_data["tracking_code"].strip()
        if not code:
            raise forms.ValidationError("کد سفارش را وارد کنید.")
        if not code.isdigit() or not (5 <= len(code) <= 7):
            raise forms.ValidationError("کد سفارش باید عددی ۵ تا ۷ رقمی باشد.")
        return code

from django import forms
from payment.models import PaymentMethodSettings

from order.models import CardToCardReceipt, City, Province
from order.services import CouponValidationError, coupon_service
from order.shipping import (
    DELIVERY_FREIGHT,
    DELIVERY_TYPE_CHOICES,
    FREIGHT_NOTES_PLACEHOLDER,
)


class CheckOutForm(forms.Form):
    delivery_type = forms.ChoiceField(
        label="روش ارسال",
        choices=DELIVERY_TYPE_CHOICES,
        initial=DELIVERY_FREIGHT,
        widget=forms.HiddenInput,
        error_messages={"required": "روش ارسال را انتخاب کنید."},
    )
    freight_province = forms.ModelChoiceField(
        label="استان مقصد",
        queryset=Province.objects.none(),
        empty_label="استان را انتخاب کنید",
        required=True,
        error_messages={
            "required": "استان مقصد را انتخاب کنید.",
            "invalid_choice": "استان انتخاب‌شده معتبر نیست.",
        },
        widget=forms.Select(
            attrs={"class": "form-select form-select-lg", "id": "freight-province"}
        ),
    )
    freight_city = forms.ModelChoiceField(
        label="شهر مقصد",
        queryset=City.objects.none(),
        empty_label="ابتدا استان را انتخاب کنید",
        required=True,
        error_messages={
            "required": "شهر مقصد را انتخاب کنید.",
            "invalid_choice": "شهر انتخاب‌شده معتبر نیست.",
        },
        widget=forms.Select(
            attrs={"class": "form-select form-select-lg", "id": "freight-city"}
        ),
    )
    freight_notes = forms.CharField(
        label="توضیحات باربری",
        required=True,
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": FREIGHT_NOTES_PLACEHOLDER,
            }
        ),
        error_messages={"required": "توضیحات باربری را برای هماهنگی ارسال وارد کنید."},
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
        self.fields["delivery_type"].initial = DELIVERY_FREIGHT

        provinces = Province.objects.filter(is_active=True)
        self.fields["freight_province"].queryset = provinces

        province_id = None
        if self.data.get("freight_province"):
            try:
                province_id = int(self.data.get("freight_province"))
            except (TypeError, ValueError):
                province_id = None
        elif self.initial.get("freight_province"):
            initial_province = self.initial["freight_province"]
            province_id = getattr(initial_province, "pk", initial_province)

        if province_id:
            self.fields["freight_city"].queryset = City.objects.filter(
                province_id=province_id,
                is_active=True,
                province__is_active=True,
            )
            self.fields["freight_city"].empty_label = "شهر را انتخاب کنید"
        else:
            self.fields["freight_city"].queryset = City.objects.none()

    def clean_freight_notes(self):
        notes = (self.cleaned_data.get("freight_notes") or "").strip()
        if not notes:
            raise forms.ValidationError(
                "توضیحات باربری را برای هماهنگی ارسال وارد کنید."
            )
        return notes

    def clean(self):
        cleaned = super().clean()
        province = cleaned.get("freight_province")
        city = cleaned.get("freight_city")
        if province and city and city.province_id != province.id:
            self.add_error("freight_city", "شهر انتخاب‌شده متعلق به این استان نیست.")
        return cleaned

    def clean_coupon(self):
        code = self.cleaned_data.get("coupon")
        if code == "":
            return None
        try:
            return coupon_service.get_valid_coupon(code=code, user=self.request.user)
        except CouponValidationError as exc:
            raise forms.ValidationError(exc.message) from exc

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


_RECEIPT_IMAGE_MAX_BYTES = 5 * 1024 * 1024


class CardToCardReceiptForm(forms.ModelForm):
    class Meta:
        model = CardToCardReceipt
        fields = ("image", "note")
        widgets = {
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "در صورت نیاز توضیح کوتاه بنویسید",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = not bool(self.instance and self.instance.pk)
        self.fields["note"].required = False
        for field in self.fields.values():
            if not field.required:
                continue
            empty_msg = f"فیلد «{field.label}» نباید خالی باشد."
            field.error_messages["required"] = empty_msg
            field.error_messages["blank"] = empty_msg
            if isinstance(field, forms.FileField):
                field.error_messages["missing"] = empty_msg
                field.error_messages["empty"] = empty_msg
        if self.is_bound:
            for name, field in self.fields.items():
                if self[name].errors:
                    css = field.widget.attrs.get("class", "")
                    if "is-invalid" not in css.split():
                        field.widget.attrs["class"] = f"{css} is-invalid".strip()

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            size = getattr(image, "size", None)
            if size and size > _RECEIPT_IMAGE_MAX_BYTES:
                raise forms.ValidationError("حجم عکس رسید باید حداکثر ۵ مگابایت باشد.")
            return image
        if self.instance and self.instance.pk and self.instance.image:
            return self.instance.image
        if self.fields["image"].required:
            raise forms.ValidationError("فیلد «عکس رسید» نباید خالی باشد.")
        return image

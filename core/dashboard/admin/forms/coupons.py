from django import forms
from order.models import CouponModel
from website.jalali_utils import format_jalali_datetime, parse_jalali_datetime

_JALALI_DT_PLACEHOLDER = "1403/01/15 - 14:30"
_JALALI_DT_ERROR = f"تاریخ را به صورت شمسی وارد کنید (مثال: {_JALALI_DT_PLACEHOLDER})."


class CouponForm(forms.ModelForm):
    expiration_date = forms.CharField(
        label="تاریخ انقضا",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _JALALI_DT_PLACEHOLDER,
                "autocomplete": "off",
                "dir": "ltr",
                "inputmode": "numeric",
                "aria-describedby": "coupon-expiration-date-help",
            },
        ),
    )

    class Meta:
        model = CouponModel
        fields = [
            "code",
            "discount_percent",
            "max_limit_usage",
            "expiration_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs["class"] = "form-control"
        self.fields["discount_percent"].widget.attrs["class"] = "form-control"
        self.fields["max_limit_usage"].widget.attrs["class"] = "form-control"

        inst = self.instance
        if inst.pk:
            self.initial["expiration_date"] = format_jalali_datetime(
                inst.expiration_date
            )

    def clean_expiration_date(self):
        raw = self.cleaned_data.get("expiration_date")
        if raw in (None, ""):
            return None
        try:
            return parse_jalali_datetime(raw)
        except ValueError as exc:
            raise forms.ValidationError(_JALALI_DT_ERROR) from exc

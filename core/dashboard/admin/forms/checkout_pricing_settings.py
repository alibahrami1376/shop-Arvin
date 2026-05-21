from django import forms

from order.models import CheckoutPricingSettings


class CheckoutPricingSettingsForm(forms.ModelForm):
    class Meta:
        model = CheckoutPricingSettings
        fields = (
            "shipping_enabled",
            "shipping_tehran_label",
            "shipping_tehran_amount",
            "shipping_province_label",
            "shipping_province_amount",
            "tax_enabled",
            "tax_percent",
        )
        widgets = {
            "shipping_tehran_amount": forms.NumberInput(attrs={"min": 0, "step": 1000}),
            "shipping_province_amount": forms.NumberInput(attrs={"min": 0, "step": 1000}),
            "tax_percent": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("shipping_enabled", "tax_enabled"):
            self.fields[name].widget.attrs.setdefault("class", "form-check-input")
        for name in (
            "shipping_tehran_label",
            "shipping_province_label",
            "shipping_tehran_amount",
            "shipping_province_amount",
            "tax_percent",
        ):
            self.fields[name].widget.attrs.setdefault("class", "form-control")

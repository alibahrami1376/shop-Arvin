from django import forms

from payment.models import PaymentMethodSettings


class PaymentMethodSettingsForm(forms.ModelForm):
    class Meta:
        model = PaymentMethodSettings
        fields = ("gateway_enabled", "card_to_card_enabled")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-check-input")

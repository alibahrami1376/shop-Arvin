from django import forms

from payment.models import CardToCardSettings


class CardToCardSettingsForm(forms.ModelForm):
    class Meta:
        model = CardToCardSettings
        fields = ["bank_name", "account_holder", "card_number", "iban", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            field = self.fields[name]
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
                field.widget.attrs.setdefault("rows", 4)
            else:
                field.widget.attrs.setdefault("class", "form-control")

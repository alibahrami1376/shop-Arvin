from django import forms

from payment.models import CardToCardSettings, RECEIPT_SOCIAL_PLATFORMS


class CardToCardSettingsForm(forms.ModelForm):
    class Meta:
        model = CardToCardSettings
        fields = [
            "bank_name",
            "account_holder",
            "card_number",
            "iban",
            "note",
            "telegram_enabled",
            "telegram_link",
            "bale_enabled",
            "bale_link",
            "rubika_enabled",
            "rubika_link",
            "whatsapp_enabled",
            "whatsapp_link",
            "email_enabled",
            "email_link",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            field = self.fields[name]
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
                field.widget.attrs.setdefault("rows", 4)
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        for key, label, _icon in RECEIPT_SOCIAL_PLATFORMS:
            enabled = cleaned.get(f"{key}_enabled")
            link = (cleaned.get(f"{key}_link") or "").strip()
            if enabled and not link:
                self.add_error(
                    f"{key}_link",
                    f"با فعال بودن {label}، وارد کردن لینک یا آدرس الزامی است.",
                )
        return cleaned

from django import forms
from payment.models import BaleBotSettings


class BaleBotSettingsForm(forms.ModelForm):
    class Meta:
        model = BaleBotSettings
        fields = (
            "bot_token",
            "provider_token",
            "bot_username",
            "webhook_secret",
            "api_base",
            "deep_link_base",
            "link_token_ttl_minutes",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bot_token"].widget = forms.PasswordInput(
            render_value=False,
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "خالی بگذارید تا مقدار قبلی حفظ شود",
            },
        )
        self.fields["bot_token"].required = False
        self.fields["webhook_secret"].widget = forms.PasswordInput(
            render_value=False,
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "خالی بگذارید تا مقدار قبلی حفظ شود",
            },
        )
        self.fields["webhook_secret"].required = False
        for name in (
            "provider_token",
            "bot_username",
            "api_base",
            "deep_link_base",
            "link_token_ttl_minutes",
        ):
            self.fields[name].widget.attrs.setdefault("class", "form-control")
        self.fields["bot_username"].widget.attrs.setdefault("placeholder", "بدون @")
        self.fields["provider_token"].widget.attrs.setdefault(
            "placeholder", "WALLET-TEST-1111111111111111"
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Preserve previous secrets when password fields submitted empty.
        if self.instance.pk:
            prev = BaleBotSettings.objects.filter(pk=self.instance.pk).first()
            if prev is not None:
                if not (self.cleaned_data.get("bot_token") or "").strip():
                    instance.bot_token = prev.bot_token
                if not (self.cleaned_data.get("webhook_secret") or "").strip():
                    instance.webhook_secret = prev.webhook_secret
        username = (instance.bot_username or "").strip().lstrip("@")
        instance.bot_username = username
        if commit:
            instance.save()
        return instance

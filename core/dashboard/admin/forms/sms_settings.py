from django import forms

from accounts.models import SMSSettings


class SMSSettingsForm(forms.ModelForm):
    class Meta:
        model = SMSSettings
        fields = ("sms_enabled",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sms_enabled"].widget.attrs.setdefault("class", "form-check-input")

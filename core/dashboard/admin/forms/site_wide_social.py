from django import forms

from website.models import SiteWideSocialSettings


class SiteWideSocialSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteWideSocialSettings
        fields = [
            "instagram_link",
            "telegram_link",
            "linkedin_link",
            "bale_link",
            "rubika_link",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
            field.widget.attrs.setdefault("dir", "ltr")

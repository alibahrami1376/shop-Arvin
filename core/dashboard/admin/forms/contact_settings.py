from django import forms

from website.models import ContactPageSettings


class ContactPageSettingsForm(forms.ModelForm):
    class Meta:
        model = ContactPageSettings
        fields = [
            "email",
            "phone",
            "working_hours",
            "instagram_link",
            "telegram_link",
            "linkedin_link",
            "bale_link",
            "rubika_link",
            "bale_channel_link",
            "bale_channel_text",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
                field.widget.attrs.setdefault("rows", 3)
            else:
                field.widget.attrs.setdefault("class", "form-control")

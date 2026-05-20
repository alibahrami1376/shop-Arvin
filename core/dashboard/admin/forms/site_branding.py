from django import forms

from website.logo_validation import SITE_LOGO_HEIGHT, SITE_LOGO_WIDTH, validate_site_logo_image
from website.models import SiteBrandingSettings


class SiteBrandingSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteBrandingSettings
        fields = ["logo", "site_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["site_name"].widget.attrs["class"] = "form-control"
        self.fields["logo"].widget.attrs["class"] = "form-control"
        self.fields["logo"].widget.attrs["accept"] = "image/png,image/webp"
        self.fields["logo"].help_text = (
            f"ابعاد دقیق: {SITE_LOGO_WIDTH}×{SITE_LOGO_HEIGHT} پیکسل — "
            "فقط PNG یا WEBP — حداکثر ۴۰۰ کیلوبایت."
        )

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if not logo:
            return logo
        if hasattr(logo, "chunks"):
            validate_site_logo_image(logo)
        return logo

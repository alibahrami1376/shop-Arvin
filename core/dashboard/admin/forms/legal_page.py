from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from website.models import LegalPage


class LegalPageForm(forms.ModelForm):
    content = forms.CharField(
        label=LegalPage._meta.get_field("content").verbose_name,
        widget=CKEditor5Widget(config_name="extends"),
    )

    class Meta:
        model = LegalPage
        fields = ["title", "content"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "form-control"
        self.fields["content"].widget = CKEditor5Widget(config_name="extends")

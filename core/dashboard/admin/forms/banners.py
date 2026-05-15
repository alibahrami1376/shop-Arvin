from django import forms

from website.models import HomeBanner


class HomeBannerForm(forms.ModelForm):
    class Meta:
        model = HomeBanner
        fields = ["title", "image", "link", "sort_order", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "form-control"
        self.fields["image"].widget.attrs["class"] = "form-control"
        self.fields["image"].widget.attrs["accept"] = (
            "image/jpeg,image/png,image/webp,image/gif,.gif"
        )
        self.fields["link"].widget.attrs["class"] = "form-control"
        self.fields["link"].widget.attrs["placeholder"] = "/shop/ یا https://..."
        self.fields["sort_order"].widget.attrs["class"] = "form-control"
        self.fields["sort_order"].widget.attrs["type"] = "number"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"
        if self.instance and self.instance.pk:
            self.fields["image"].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk and not self.files.get("image"):
            instance.image = self.instance.image
        if commit:
            instance.save()
        return instance

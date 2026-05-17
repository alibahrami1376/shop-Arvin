from django import forms

from website.models import HomeBanner


class HomeBannerForm(forms.ModelForm):
    class Meta:
        model = HomeBanner
        fields = [
            "title",
            "subtitle",
            "button_text",
            "image",
            "image_alt",
            "link",
            "background_style",
            "display_target",
            "sort_order",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in (
            "title",
            "subtitle",
            "button_text",
            "image_alt",
            "link",
            "sort_order",
            "background_style",
            "display_target",
        ):
            if name in self.fields:
                self.fields[name].widget.attrs["class"] = "form-control"
        if "display_target" in self.fields:
            self.fields["display_target"].widget.attrs["class"] = "form-select"
        self.fields["subtitle"].widget.attrs["rows"] = 3
        self.fields["image"].widget.attrs["class"] = "form-control"
        self.fields["image"].widget.attrs["accept"] = (
            "image/jpeg,image/png,image/webp,image/gif,.gif"
        )
        self.fields["link"].widget.attrs["placeholder"] = "/shop/product/grid/"
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


class DefaultHomeBannerForm(forms.ModelForm):
    class Meta:
        model = HomeBanner
        fields = ["is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"

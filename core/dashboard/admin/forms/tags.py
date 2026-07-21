from django import forms
from django.utils.text import slugify

from shop.models import ProductTagModel


class ProductTagForm(forms.ModelForm):
    class Meta:
        model = ProductTagModel
        fields = ["title", "slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "form-control"
        self.fields["slug"].widget.attrs["class"] = "form-control"
        self.fields["slug"].required = False
        self.fields["slug"].widget.attrs.setdefault(
            "placeholder", "در صورت خالی بودن، خودکار ساخته می‌شود"
        )

    def clean_slug(self):
        raw_slug = (self.cleaned_data.get("slug") or "").strip()
        if raw_slug:
            return raw_slug

        title = (self.cleaned_data.get("title") or "").strip()
        base_slug = slugify(title, allow_unicode=True)
        if not base_slug:
            return raw_slug

        slug = base_slug
        i = 2
        qs = ProductTagModel.objects.all()
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"
            i += 1
        return slug

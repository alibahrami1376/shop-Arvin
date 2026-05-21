from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from shop.models import ProductCategoryModel


class CategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryModel
        fields = ["title", "slug", "parent"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "form-control"
        self.fields["slug"].widget.attrs["class"] = "form-control"
        self.fields["slug"].required = False
        self.fields["slug"].widget.attrs.setdefault("placeholder", "در صورت خالی بودن، خودکار ساخته می‌شود")
        self.fields["parent"].widget.attrs["class"] = "form-select"
        self.fields["parent"].required = False
        self.fields["parent"].empty_label = "بدون والد (دسته اصلی)"

        invalid_ids = set()
        if self.instance and self.instance.pk:
            invalid_ids = set(self.instance.get_self_and_descendant_ids())
        valid_pks = [
            cat.pk
            for cat in ProductCategoryModel.get_tree_ordered()
            if cat.pk not in invalid_ids
        ]
        self.fields["parent"].queryset = ProductCategoryModel.objects.filter(pk__in=valid_pks)
        self.fields["parent"].label_from_instance = lambda obj: obj.get_indented_title()

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if not parent or not self.instance.pk:
            return parent
        if parent.pk == self.instance.pk:
            raise ValidationError("دسته نمی‌تواند والد خودش باشد.")
        if parent.pk in self.instance.get_self_and_descendant_ids():
            raise ValidationError("دسته نمی‌تواند زیرمجموعه خودش باشد.")
        return parent

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
        qs = ProductCategoryModel.objects.all()
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"
            i += 1
        return slug


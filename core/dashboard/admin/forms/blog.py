from blog.models import Category as BlogCategory
from blog.models import Post, PostImageModel
from blog.models import Tag as BlogTag
from django import forms
from django.forms import inlineformset_factory
from django_ckeditor_5.widgets import CKEditor5Widget
from website.jalali_utils import format_jalali_datetime, parse_jalali_datetime

_JALALI_DT_PLACEHOLDER = "1403/01/15 - 14:30"
_JALALI_DT_ERROR = f"تاریخ را به صورت شمسی وارد کنید (مثال: {_JALALI_DT_PLACEHOLDER})."


class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["class"] = "form-control"


class BlogTagForm(forms.ModelForm):
    class Meta:
        model = BlogTag
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["class"] = "form-control"


class BlogPostForm(forms.ModelForm):
    """فیلد content صریح است تا حتماً CKEditor5Widget اعمال شود (نه Textarea پیش‌فرض)."""

    content = forms.CharField(
        label=Post._meta.get_field("content").verbose_name,
        widget=CKEditor5Widget(config_name="extends"),
    )
    published_date = forms.CharField(
        label=Post._meta.get_field("published_date").verbose_name,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _JALALI_DT_PLACEHOLDER,
                "autocomplete": "off",
                "dir": "ltr",
                "inputmode": "numeric",
                "aria-describedby": "blog-published-date-help",
            },
        ),
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "content",
            "image",
            "image_alt",
            "url",
            "category",
            "tags",
            "status",
            "published_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget = CKEditor5Widget(config_name="extends")
        for fname in ("title", "slug", "image", "image_alt", "url"):
            self.fields[fname].widget.attrs.setdefault("class", "form-control")
        self.fields["image_alt"].widget.attrs.setdefault(
            "placeholder", "اگر خالی باشد، عنوان پست استفاده می‌شود"
        )
        self.fields["slug"].required = False
        self.fields["slug"].widget.attrs.setdefault(
            "placeholder", "در صورت خالی بودن، از عنوان ساخته می‌شود"
        )
        self.fields["category"].widget.attrs.setdefault("class", "form-select")
        self.fields["tags"].widget.attrs.setdefault("class", "form-select")
        self.fields["tags"].required = False
        self.fields["status"].widget.attrs.setdefault("class", "form-check-input")
        self.fields["url"].required = False

        inst = self.instance
        if inst.pk:
            self.initial["published_date"] = format_jalali_datetime(inst.published_date)

    def clean_published_date(self):
        raw = self.cleaned_data.get("published_date")
        if raw in (None, ""):
            return None
        try:
            return parse_jalali_datetime(raw)
        except ValueError as exc:
            raise forms.ValidationError(_JALALI_DT_ERROR) from exc

    def clean_slug(self):
        from blog.utils import unique_post_slug
        from django.utils.text import slugify

        raw = (self.cleaned_data.get("slug") or "").strip()
        title = self.cleaned_data.get("title") or getattr(self.instance, "title", "")
        if raw:
            base = slugify(raw, allow_unicode=True) or raw
            slug = base
            qs = Post.objects.all()
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            i = 2
            while qs.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            return slug
        return unique_post_slug(title, exclude_pk=self.instance.pk)


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImageModel
        fields = ["file", "image_alt"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs.setdefault("class", "form-control")
        self.fields["image_alt"].required = False
        self.fields["image_alt"].widget.attrs.setdefault("class", "form-control")
        self.fields["image_alt"].widget.attrs.setdefault(
            "placeholder", "متن alt (اختیاری)"
        )


PostImageFormSet = inlineformset_factory(
    Post,
    PostImageModel,
    form=PostImageForm,
    extra=5,
    can_delete=True,
    max_num=20,
)

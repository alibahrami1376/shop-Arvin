from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from django_ckeditor_5.widgets import CKEditor5Widget

from blog.models import Category as BlogCategory
from blog.models import Post, PostImageModel, Tag as BlogTag

_DATETIME_LOCAL_INPUT_FORMATS = (
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
)


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

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "image",
            "url",
            "category",
            "tags",
            "status",
            "published_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget = CKEditor5Widget(config_name="extends")
        for fname in ("title", "image", "url"):
            self.fields[fname].widget.attrs.setdefault("class", "form-control")
        self.fields["category"].widget.attrs.setdefault("class", "form-select")
        self.fields["tags"].widget.attrs.setdefault("class", "form-select")
        self.fields["tags"].required = False
        self.fields["status"].widget.attrs.setdefault("class", "form-check-input")
        self.fields["url"].required = False

        pub = self.fields["published_date"]
        pub.required = False
        pub.input_formats = list(_DATETIME_LOCAL_INPUT_FORMATS)
        pub.widget = forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "step": "60",
                "autocomplete": "off",
                "aria-describedby": "blog-published-date-help",
            },
        )
        inst = self.instance
        if inst.pk and inst.published_date:
            dt = inst.published_date
            if timezone.is_aware(dt):
                dt = timezone.localtime(dt)
            self.initial["published_date"] = dt.strftime("%Y-%m-%dT%H:%M")


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImageModel
        fields = ["file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs.setdefault("class", "form-control")


PostImageFormSet = inlineformset_factory(
    Post,
    PostImageModel,
    form=PostImageForm,
    extra=5,
    can_delete=True,
    max_num=20,
)

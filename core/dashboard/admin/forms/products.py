from decimal import Decimal, InvalidOperation

from django import forms
from django.forms import inlineformset_factory
from django_ckeditor_5.widgets import CKEditor5Widget
from shop.models import ProductImageModel, ProductModel

_DIGIT_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_price_input(value):
    if value is None or isinstance(value, int | float | Decimal):
        return value
    text = str(value).translate(_DIGIT_TRANSLATION)
    text = (
        text.replace(",", "").replace("٬", "").replace(" ", "").replace("_", "").strip()
    )
    return text


class ThousandSeparatedDecimalField(forms.DecimalField):
    """Accepts 1,250,000 in the widget; stores a plain decimal."""

    def to_python(self, value):
        return super().to_python(normalize_price_input(value))

    def prepare_value(self, value):
        if value in self.empty_values:
            return value
        if isinstance(value, str) and any(ch in value for ch in ",٬"):
            return value
        try:
            number = int(Decimal(str(normalize_price_input(value))))
        except (InvalidOperation, ValueError, TypeError):
            return value
        return f"{number:,}"


class ProductForm(forms.ModelForm):
    clear_image_crop = forms.BooleanField(
        required=False,
        label="حذف برش دیتیل و استفاده از فایل اصلی",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    clear_card_image_crop = forms.BooleanField(
        required=False,
        label="حذف برش کارت و استفاده از فایل کارت/اصلی",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    clear_card_image = forms.BooleanField(
        required=False,
        label="حذف تصویر کارت (بازگشت به تصویر اصلی بدون برش)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    description = forms.CharField(
        label="توضیحات",
        widget=CKEditor5Widget(config_name="extends"),
    )
    price = ThousandSeparatedDecimalField(
        label="قیمت",
        max_digits=10,
        decimal_places=0,
        min_value=0,
        widget=forms.TextInput(
            attrs={
                "class": "form-control js-price-thousands",
                "inputmode": "numeric",
                "autocomplete": "off",
                "dir": "ltr",
            }
        ),
    )

    class Meta:
        model = ProductModel
        fields = [
            "title",
            "slug",
            "stock",
            "status",
            "category",
            "tags",
            "price",
            "discount_percent",
            "brief_description",
            "description",
            "image",
            "image_crop",
            "image_alt",
            "card_image",
            "card_image_crop",
            "card_image_alt",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget = CKEditor5Widget(config_name="extends")
        self.fields["title"].widget.attrs["class"] = "form-control"
        self.fields["slug"].widget.attrs["class"] = "form-control"
        self.fields["category"].widget.attrs["class"] = "form-control"
        self.fields["category"].label_from_instance = lambda obj: (
            obj.get_indented_title()
        )
        self.fields["tags"].widget.attrs["class"] = "form-control"
        self.fields["tags"].required = False
        for name in ("image", "image_crop", "card_image", "card_image_crop"):
            self.fields[name].widget.attrs["class"] = "form-control"
            self.fields[name].required = False
        self.fields["image"].required = False
        self.fields["image_alt"].widget.attrs["class"] = "form-control"
        self.fields["image_alt"].widget.attrs["placeholder"] = (
            "توضیح کوتاه عکس برای دسترسی‌پذیری"
        )
        self.fields["card_image_alt"].widget.attrs["class"] = "form-control"
        self.fields["card_image_alt"].widget.attrs["placeholder"] = (
            "اگر خالی باشد از alt تصویر اصلی استفاده می‌شود"
        )
        self.fields["card_image_alt"].required = False
        self.fields["brief_description"].widget.attrs["class"] = "form-control"
        self.fields["stock"].widget.attrs["class"] = "form-control"
        self.fields["stock"].widget.attrs["type"] = "number"
        self.fields["status"].widget.attrs["class"] = "form-select"
        self.fields["discount_percent"].widget.attrs["class"] = "form-control"
        # Hidden crop file inputs are filled by Cropper.js before submit.
        self.fields["image_crop"].widget.attrs["class"] = (
            "form-control js-crop-file d-none"
        )
        self.fields["image_crop"].widget.attrs["data-crop-for"] = "detail"
        self.fields["card_image_crop"].widget.attrs["class"] = (
            "form-control js-crop-file d-none"
        )
        self.fields["card_image_crop"].widget.attrs["data-crop-for"] = "card"

    def clean(self):
        cleaned = super().clean()
        if self.instance and self.instance.pk:
            # Keep existing main image when edit form omits a new upload.
            if not cleaned.get("image") and self.instance.image:
                cleaned["image"] = self.instance.image
        elif not cleaned.get("image"):
            self.add_error("image", "تصویر اصلی دیتیل الزامی است.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("clear_image_crop") and instance.image_crop:
            instance.image_crop.delete(save=False)
            instance.image_crop = None
        if self.cleaned_data.get("clear_card_image_crop") and instance.card_image_crop:
            instance.card_image_crop.delete(save=False)
            instance.card_image_crop = None
        if self.cleaned_data.get("clear_card_image"):
            if instance.card_image:
                instance.card_image.delete(save=False)
                instance.card_image = None
            if instance.card_image_crop:
                instance.card_image_crop.delete(save=False)
                instance.card_image_crop = None
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImageModel
        fields = ["file", "image_alt", "sort_order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs["class"] = "form-control"
        self.fields["image_alt"].widget.attrs["class"] = "form-control"
        self.fields["image_alt"].required = False
        self.fields["image_alt"].widget.attrs["placeholder"] = "متن alt (اختیاری)"
        self.fields["sort_order"].widget = forms.HiddenInput()
        self.fields["sort_order"].required = False


# Formset برای آپلود چند عکس
ProductImageFormSet = inlineformset_factory(
    ProductModel,
    ProductImageModel,
    form=ProductImageForm,
    extra=5,  # تعداد فیلد خالی برای آپلود
    can_delete=True,
    max_num=10,  # حداکثر تعداد عکس اضافی
)

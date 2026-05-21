from django import forms
from django.forms import inlineformset_factory
from django_ckeditor_5.widgets import CKEditor5Widget

from shop.models import ProductModel, ProductImageModel, ProductCategoryModel


class ProductForm(forms.ModelForm):
    description = forms.CharField(
        label="توضیحات",
        widget=CKEditor5Widget(config_name="extends"),
    )

    class Meta:
        model = ProductModel
        fields = [
            "title",
            "slug",
            "stock",
            "status",
            "category",
            "price",
            "discount_percent",
            "brief_description",
            "description",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget = CKEditor5Widget(config_name="extends")
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['category'].label_from_instance = lambda obj: obj.get_indented_title()
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['brief_description'].widget.attrs['class'] = 'form-control'
        self.fields['stock'].widget.attrs['class'] = 'form-control'
        self.fields['stock'].widget.attrs['type'] = 'number'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs['class'] = 'form-control'

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImageModel
        fields = ['file']


# Formset برای آپلود چند عکس
ProductImageFormSet = inlineformset_factory(
    ProductModel,
    ProductImageModel,
    form=ProductImageForm,
    extra=5,  # تعداد فیلد خالی برای آپلود
    can_delete=True,
    max_num=10  # حداکثر تعداد عکس اضافی
)

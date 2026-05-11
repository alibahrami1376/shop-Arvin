from django import forms
from django.forms import inlineformset_factory
from shop.models import ProductModel, ProductImageModel


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['title', 'slug', 'stock', 'status', 'category', 'price', 'discount_percent', 'brief_description', 'description', 'image']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['brief_description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['id'] = 'ckeditor'
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

from django import forms
from .models import ReviewModel
from shop.models import ProductModel,ProductStatusType

class SubmitReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ['product','rate', 'description']
        error_messages = {
            "description": {
                "required": "متن دیدگاه را وارد کنید.",
            },
            "rate": {
                "required": "امتیاز را انتخاب کنید.",
                "invalid_choice": "امتیاز انتخاب‌شده معتبر نیست.",
            },
            "product": {
                "required": "محصول مشخص نیست.",
                "invalid_choice": "محصول انتخاب‌شده معتبر نیست.",
            },
        }
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')

        # Check if the product exists and is published
        try:
            ProductModel.objects.get(id=product.id,status=ProductStatusType.publish.value)
        except ProductModel.DoesNotExist:
            raise forms.ValidationError("این محصول وجود ندارد")

        return cleaned_data
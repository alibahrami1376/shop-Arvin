from django import forms

from accounts.validators import validate_iranian_cellphone_number

from .models import ContactModel, NewsLetter


class ContactForm(forms.ModelForm):
    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "۰۹۱۲۳۴۵۶۷۸۹",
                "dir": "ltr",
                "inputmode": "tel",
                "class": "form-control form-control-lg text-center",
            }
        ),
    )

    class Meta:
        model = ContactModel
        fields = ["subject", "full_name", "email", "phone_number", "content"]
        
        error_messages = {
            "email": {
                "required": "ایمیل را وارد کنید.",
                "invalid": "آدرس ایمیل معتبر نیست.",
            },
            "content": {
                "required": "متن پیام را وارد کنید.",
                "min_length": "متن پیام خیلی کوتاه است.",
            },
            "subject": {
                "required": "موضوع پیام را وارد کنید.",
            },
            "full_name": {
                "required": "نام و نام خانوادگی را وارد کنید.",
            },
        }

    def clean_phone_number(self):
        value = (self.cleaned_data.get("phone_number") or "").strip()
        if not value:
            return None
        return validate_iranian_cellphone_number(value)


class NewsLetterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=False)
    class Meta:
        model = NewsLetter
        fields = ['email',"first_name"]

    def clean_first_name(self):
        if len(self.cleaned_data['first_name']) > 0:
            raise forms.ValidationError("این فیلد باید خالی بماند.")
        return self.cleaned_data['first_name']
    
    def save(self, commit=True):
        newsletter, created = NewsLetter.objects.get_or_create(email=self.cleaned_data.get("email"))
        return newsletter


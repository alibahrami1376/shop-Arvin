from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "email",
            "is_active",
            "is_verified",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add custom classes to fields
        self.fields['email'].widget.attrs['class'] = 'form-control mx-3 Disabled text-center mb-3'

        self.fields['is_active'].widget.attrs['class'] = 'form-check-input mb-3'
        self.fields['is_verified'].widget.attrs['class'] = 'form-check-input mb-3'


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "form-control mb-3"}),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "form-control mb-3"}),
    )

    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "is_active",
            "is_verified",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False
        self.fields["phone_number"].required = False
        self.fields["email"].widget.attrs["class"] = "form-control mb-3"
        self.fields["phone_number"].widget.attrs["class"] = "form-control mb-3"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input mb-3"
        self.fields["is_verified"].widget.attrs["class"] = "form-check-input mb-3"

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email") or None
        phone_number = cleaned_data.get("phone_number") or None
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not email and not phone_number:
            raise forms.ValidationError("حداقل یکی از ایمیل یا شماره موبایل الزامی است.")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "رمز عبور و تکرار آن یکسان نیستند.")

        cleaned_data["email"] = email
        cleaned_data["phone_number"] = phone_number
        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data.get("email")
        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data["password1"]
        user = User.objects.create_customer(
            email=email,
            phone_number=phone_number,
            password=password,
            phone_verified=bool(phone_number),
            is_active=self.cleaned_data.get("is_active", True),
            is_verified=self.cleaned_data.get("is_verified", False),
        )
        return user
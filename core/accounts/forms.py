from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class AuthenticationForm(auth_forms.AuthenticationForm):
    def confirm_login_allowed(self, user):
        super(AuthenticationForm, self).confirm_login_allowed(user)
        # if not user.is_verified:
        #     raise ValidationError("user is not verified")


class UserRegistrationForm(forms.Form):
    """فرم ثبت‌نام با ایمیل، نام، نام خانوادگی، موبایل و رمز عبور."""

    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg text-center", "placeholder": "email@site.com"}),
    )
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg text-center", "placeholder": "حداقل ۸ کاراکتر"}),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg text-center", "placeholder": "تکرار رمز عبور"}),
    )
    first_name = forms.CharField(
        label="نام",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg text-center", "placeholder": "نام"}),
    )
    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg text-center", "placeholder": "نام خانوادگی"}),
    )
    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=12,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg text-center", "placeholder": "۰۹۱۲۳۴۵۶۷۸۹"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_phone_number(self):
        from accounts.validators import validate_iranian_cellphone_number
        value = self.cleaned_data.get("phone_number")
        validate_iranian_cellphone_number(value)
        return value

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError({"password2": "رمز عبور و تکرار آن یکسان نیستند."})
        return cleaned_data
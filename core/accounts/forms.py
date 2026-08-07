from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from core.forms_persian import translate_error_message

User = get_user_model()


class AuthenticationForm(auth_forms.AuthenticationForm):
    error_messages = {
        "invalid_login": "ایمیل/موبایل یا رمز عبور اشتباه است.",
        "inactive": "این حساب غیرفعال است.",
    }
    username = auth_forms.UsernameField(
        label="ایمیل یا شماره موبایل",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "class": "form-control form-control-lg text-center",
                "placeholder": "email@site.com یا ۰۹۱۲...",
                "dir": "ltr",
            }
        ),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)


class UserRegistrationForm(forms.Form):
    """ثبت‌نام با ایمیل و رمز عبور."""

    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "email@site.com",
                "dir": "ltr",
                "autocomplete": "email",
            }
        ),
    )
    first_name = forms.CharField(
        label="نام",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "نام",
            }
        ),
    )
    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "نام خانوادگی",
            }
        ),
    )
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "حداقل ۸ کاراکتر",
            }
        ),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "تکرار رمز عبور",
            }
        ),
    )

    def clean_email(self):
        value = (self.cleaned_data.get("email") or "").strip()
        if not value:
            raise ValidationError("ایمیل را وارد کنید.")
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            try:
                validate_password(password)
            except ValidationError as exc:
                raise ValidationError(
                    [translate_error_message(msg) for msg in exc.messages]
                ) from exc
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError({"password2": "رمز عبور و تکرار آن یکسان نیستند."})
        return cleaned_data

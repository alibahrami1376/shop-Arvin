from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from core.forms_persian import translate_error_message
from django.utils import timezone

from accounts.models import OTPCode
from accounts.utils import sms_otp_enabled

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
    """ثبت‌نام با شماره موبایل؛ در صورت فعال بودن OTP، کد پیامک الزامی است."""

    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "۰۹۱۲۳۴۵۶۷۸۹",
                "dir": "ltr",
                "inputmode": "tel",
            }
        ),
    )
    otp_code = forms.CharField(
        label="کد تأیید پیامک",
        max_length=6,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "۶ رقم",
                "dir": "ltr",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
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

    def __init__(self, *args, require_otp=None, otp_expires_at=None, otp_session_phone=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.require_otp = sms_otp_enabled() if require_otp is None else require_otp
        self.otp_expires_at = otp_expires_at
        self.otp_session_phone = otp_session_phone
        if not self.require_otp:
            self.fields["otp_code"].widget = forms.HiddenInput()
            self.fields["otp_code"].required = False

    def clean_phone_number(self):
        value = self.cleaned_data.get("phone_number")
        phone = User.objects.normalize_phone(value)
        if User.objects.filter(phone_number=phone).exists():
            raise ValidationError("این شماره موبایل قبلاً ثبت شده است.")
        return phone

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

        if self.require_otp:
            phone = cleaned_data.get("phone_number")
            if (
                self.otp_session_phone
                and phone
                and phone != self.otp_session_phone
            ):
                raise ValidationError(
                    {
                        "phone_number": (
                            "شماره موبایل تغییر کرده است. دوباره «دریافت کد تأیید» را بزنید."
                        )
                    }
                )
            if self.otp_expires_at and timezone.now().timestamp() > float(
                self.otp_expires_at
            ):
                raise ValidationError(
                    {
                        "otp_code": (
                            f"زمان وارد کردن کد ({OTPCode.VALIDITY_MINUTES} دقیقه) "
                            "تمام شده است. دوباره «دریافت کد تأیید» را بزنید."
                        )
                    }
                )
            if not (cleaned_data.get("otp_code") or "").strip():
                raise ValidationError(
                    {"otp_code": "برای ثبت‌نام، کد تأیید پیامک را وارد کنید."}
                )
        return cleaned_data

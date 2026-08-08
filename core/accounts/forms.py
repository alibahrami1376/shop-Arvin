from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from core.forms_persian import translate_error_message

from accounts.models import OTPCode
from accounts.utils import get_valid_otp

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
    """ثبت‌نام با انتخاب روش: ایمیل یا موبایل (+ OTP برای موبایل)."""

    REGISTER_EMAIL = "email"
    REGISTER_PHONE = "phone"

    register_method = forms.ChoiceField(
        choices=(
            (REGISTER_EMAIL, "ایمیل"),
            (REGISTER_PHONE, "موبایل"),
        ),
        widget=forms.HiddenInput(),
        initial=REGISTER_EMAIL,
    )
    email = forms.EmailField(
        label="ایمیل",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "email@site.com",
                "dir": "ltr",
                "autocomplete": "email",
            }
        ),
    )
    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=20,
        required=False,
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

    def __init__(self, *args, otp_expires_at=None, otp_session_phone=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.otp_expires_at = otp_expires_at
        self.otp_session_phone = otp_session_phone

    def clean_email(self):
        value = (self.cleaned_data.get("email") or "").strip()
        if not value:
            return None
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_phone_number(self):
        value = (self.cleaned_data.get("phone_number") or "").strip()
        if not value:
            return None
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

        method = cleaned_data.get("register_method") or self.REGISTER_EMAIL
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone_number")

        if method == self.REGISTER_EMAIL:
            if not email:
                raise ValidationError({"email": "ایمیل را وارد کنید."})
            cleaned_data["phone_number"] = None
            cleaned_data["otp_code"] = None
            return cleaned_data

        if method != self.REGISTER_PHONE:
            raise ValidationError("روش ثبت‌نام نامعتبر است.")

        if not phone:
            raise ValidationError({"phone_number": "شماره موبایل را وارد کنید."})
        cleaned_data["email"] = None

        if (
            self.otp_session_phone
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
        otp_code = (cleaned_data.get("otp_code") or "").strip()
        if not otp_code:
            raise ValidationError(
                {"otp_code": "برای ثبت‌نام با موبایل، کد تأیید پیامک را وارد کنید."}
            )
        try:
            cleaned_data["_otp"] = get_valid_otp(phone, otp_code)
        except ValidationError as exc:
            msg = exc.messages[0] if getattr(exc, "messages", None) else str(exc)
            raise ValidationError({"otp_code": msg}) from exc
        return cleaned_data


class PasswordResetForm(forms.Form):
    """بازیابی رمز عبور با موبایل + OTP + رمز جدید."""

    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "۰۹۱۲۳۴۵۶۷۸۹",
                "dir": "ltr",
                "inputmode": "tel",
                "autocomplete": "tel",
            }
        ),
    )
    otp_code = forms.CharField(
        label="کد تأیید پیامک",
        max_length=6,
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
    password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "حداقل ۸ کاراکتر",
                "autocomplete": "new-password",
            }
        ),
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "placeholder": "تکرار رمز عبور",
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, *args, otp_expires_at=None, otp_session_phone=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.otp_expires_at = otp_expires_at
        self.otp_session_phone = otp_session_phone

    def clean_phone_number(self):
        value = (self.cleaned_data.get("phone_number") or "").strip()
        if not value:
            raise ValidationError("شماره موبایل را وارد کنید.")
        phone = User.objects.normalize_phone(value)
        if not User.objects.filter(phone_number=phone).exists():
            raise ValidationError("حسابی با این شماره موبایل یافت نشد.")
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

        phone = cleaned_data.get("phone_number")
        if not phone:
            return cleaned_data

        if self.otp_session_phone and phone != self.otp_session_phone:
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

        otp_code = (cleaned_data.get("otp_code") or "").strip()
        if not otp_code:
            raise ValidationError(
                {"otp_code": "کد تأیید پیامک را وارد کنید."}
            )
        try:
            cleaned_data["_otp"] = get_valid_otp(phone, otp_code)
            cleaned_data["_user"] = User.objects.get(phone_number=phone)
        except ValidationError as exc:
            msg = exc.messages[0] if getattr(exc, "messages", None) else str(exc)
            raise ValidationError({"otp_code": msg}) from exc
        return cleaned_data

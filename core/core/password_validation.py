from django.contrib.auth.password_validation import (
    CommonPasswordValidator,
    MinimumLengthValidator,
    NumericPasswordValidator,
    UserAttributeSimilarityValidator,
)
from django.core.exceptions import ValidationError


class PersianMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError as exc:
            raise ValidationError(
                f"رمز عبور باید حداقل {self.min_length} کاراکتر باشد.",
                code=exc.code,
                params=exc.params,
            ) from exc


class PersianUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "رمز عبور نباید بیش از حد شبیه به اطلاعات حساب کاربری شما باشد.",
                code="password_too_similar",
            )


class PersianCommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "این رمز عبور بسیار ساده و رایج است؛ رمز قوی‌تری انتخاب کنید.",
                code="password_too_common",
            )


class PersianNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "رمز عبور نباید فقط از عدد تشکیل شود.",
                code="password_entirely_numeric",
            )


class ASCIIOnlyPasswordValidator:
    def validate(self, password, user=None):
        if any(ord(ch) > 127 for ch in password):
            raise ValidationError(
                "رمز عبور باید فقط شامل حروف انگلیسی، اعداد و نمادهای استاندارد باشد."
            )

    def get_help_text(self):
        return "رمز عبور نباید شامل حروف فارسی یا سایر کاراکترهای یونیکد باشد."
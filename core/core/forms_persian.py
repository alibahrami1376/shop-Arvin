"""
پیام‌های پیش‌فرض فارسی برای فرم‌ها و API.
"""

from django import forms
from django.forms import models as model_forms

# پیام‌های رایج فیلدهای Django
DEFAULT_FIELD_ERROR_MESSAGES = {
    "required": "پر کردن این فیلد الزامی است.",
    "invalid": "مقدار وارد شده معتبر نیست.",
    "invalid_choice": "گزینه انتخاب‌شده معتبر نیست.",
    "null": "این فیلد نمی‌تواند خالی باشد.",
    "blank": "پر کردن این فیلد الزامی است.",
    "unique": "این مقدار قبلاً ثبت شده است.",
    "unique_for_date": "برای این تاریخ قبلاً ثبت شده است.",
    "max_length": "حداکثر %(limit_value)s کاراکتر مجاز است (%(show_value)s کاراکتر وارد شده).",
    "min_length": "حداقل %(limit_value)s کاراکتر لازم است (%(show_value)s کاراکتر وارد شده).",
    "max_value": "مقدار باید حداکثر %(limit_value)s باشد.",
    "min_value": "مقدار باید حداقل %(limit_value)s باشد.",
    "max_digits": "تعداد ارقام بیش از حد مجاز است.",
    "decimal_places": "تعداد اعشار بیش از حد مجاز است.",
    "invalid_image": "فایل تصویر معتبر نیست.",
    "invalid_extension": "پسوند فایل مجاز نیست.",
    "empty": "حداقل یک مورد انتخاب کنید.",
    "overflow": "عدد وارد شده بیش از حد بزرگ است.",
}

# فیلدهای تخصصی
EMAIL_FIELD_ERROR_MESSAGES = {
    **DEFAULT_FIELD_ERROR_MESSAGES,
    "invalid": "آدرس ایمیل معتبر نیست.",
}

INTEGER_FIELD_ERROR_MESSAGES = {
    **DEFAULT_FIELD_ERROR_MESSAGES,
    "invalid": "عدد وارد شده معتبر نیست.",
}

URL_FIELD_ERROR_MESSAGES = {
    **DEFAULT_FIELD_ERROR_MESSAGES,
    "invalid": "آدرس اینترنتی معتبر نیست.",
}

DATE_FIELD_ERROR_MESSAGES = {
    **DEFAULT_FIELD_ERROR_MESSAGES,
    "invalid": "تاریخ وارد شده معتبر نیست.",
}

DATETIME_FIELD_ERROR_MESSAGES = {
    **DEFAULT_FIELD_ERROR_MESSAGES,
    "invalid": "تاریخ و زمان وارد شده معتبر نیست.",
}

FILE_FIELD_ERROR_MESSAGES = {
    **DEFAULT_FIELD_ERROR_MESSAGES,
    "invalid": "فایل انتخاب‌شده معتبر نیست.",
    "missing": "فایلی انتخاب نشده است.",
    "empty": "فایل انتخاب‌شده خالی است.",
    "max_length": "نام فایل بیش از حد طولانی است.",
}

# فرم‌های احراز هویت Django
AUTH_FORM_ERROR_MESSAGES = {
    "invalid_login": "ایمیل/موبایل یا رمز عبور اشتباه است.",
    "inactive": "این حساب غیرفعال است.",
    "password_mismatch": "رمز عبور جدید و تکرار آن یکسان نیستند.",
    "password_incorrect": "رمز عبور فعلی اشتباه است.",
}

# نگاشت پیام‌های انگلیسی رایج (پشتیبان برای خطاهای کتابخانه‌ها)
ENGLISH_TO_PERSIAN = {
    "This field is required.": "پر کردن این فیلد الزامی است.",
    "This field cannot be null.": "این فیلد نمی‌تواند خالی باشد.",
    "This field cannot be blank.": "پر کردن این فیلد الزامی است.",
    "Enter a valid email address.": "آدرس ایمیل معتبر نیست.",
    "Enter a valid URL.": "آدرس اینترنتی معتبر نیست.",
    "Enter a valid integer.": "عدد وارد شده معتبر نیست.",
    "Enter a valid number.": "عدد وارد شده معتبر نیست.",
    "Enter a valid date.": "تاریخ وارد شده معتبر نیست.",
    "Enter a valid time.": "زمان وارد شده معتبر نیست.",
    "Enter a valid date/time.": "تاریخ و زمان وارد شده معتبر نیست.",
    "Enter a valid value.": "مقدار وارد شده معتبر نیست.",
    "Select a valid choice. That choice is not one of the available choices.": (
        "گزینه انتخاب‌شده معتبر نیست."
    ),
    "Select a valid choice. %(value)s is not one of the available choices.": (
        "گزینه «%(value)s» در لیست گزینه‌های مجاز نیست."
    ),
    "Ensure this value is less than or equal to %(limit_value)s.": (
        "مقدار باید حداکثر %(limit_value)s باشد."
    ),
    "Ensure this value is greater than or equal to %(limit_value)s.": (
        "مقدار باید حداقل %(limit_value)s باشد."
    ),
    "Ensure this field has no more than %(max)s character.": (
        "حداکثر %(max)s کاراکتر مجاز است."
    ),
    "Ensure this field has no more than %(max)s characters.": (
        "حداکثر %(max)s کاراکتر مجاز است."
    ),
    "Ensure this field has at least %(min)s character.": (
        "حداقل %(min)s کاراکتر لازم است."
    ),
    "Ensure this field has at least %(min)s characters.": (
        "حداقل %(min)s کاراکتر لازم است."
    ),
    "Ensure this value has at least %(limit_value)s character (it has %(show_value)s).": (
        "حداقل %(limit_value)s کاراکتر لازم است (%(show_value)s کاراکتر وارد شده)."
    ),
    "Ensure this value has at least %(limit_value)s characters (it has %(show_value)s).": (
        "حداقل %(limit_value)s کاراکتر لازم است (%(show_value)s کاراکتر وارد شده)."
    ),
    "Ensure this value has at most %(limit_value)s character (it has %(show_value)s).": (
        "حداکثر %(limit_value)s کاراکتر مجاز است (%(show_value)s کاراکتر وارد شده)."
    ),
    "Ensure this value has at most %(limit_value)s characters (it has %(show_value)s).": (
        "حداکثر %(limit_value)s کاراکتر مجاز است (%(show_value)s کاراکتر وارد شده)."
    ),
    "File extension “%(extension)s” is not allowed. Allowed extensions are: %(allowed_extensions)s.": (
        "پسوند فایل «%(extension)s» مجاز نیست. پسوندهای مجاز: %(allowed_extensions)s"
    ),
    "The submitted file is empty.": "فایل انتخاب‌شده خالی است.",
    "No file was submitted. Check the encoding type on the form.": "فایلی ارسال نشده است.",
    "Please enter a correct username and password. Note that both fields may be case-sensitive.": (
        "ایمیل/موبایل یا رمز عبور اشتباه است."
    ),
    "Please enter a correct username and password.": "ایمیل/موبایل یا رمز عبور اشتباه است.",
    "This account is inactive.": "این حساب غیرفعال است.",
    "The password is too similar to the %(verbose_name)s.": (
        "رمز عبور بیش از حد شبیه به %(verbose_name)s است."
    ),
    "This password is too short. It must contain at least %(min_length)d characters.": (
        "رمز عبور باید حداقل %(min_length)d کاراکتر باشد."
    ),
    "This password is too short. It must contain at least 8 characters.": (
        "رمز عبور باید حداقل ۸ کاراکتر باشد."
    ),
    "This password is too common.": "این رمز عبور بسیار ساده و رایج است.",
    "This password is entirely numeric.": "رمز عبور نباید فقط از عدد تشکیل شود.",
    "The two password fields didn't match.": "رمز عبور و تکرار آن یکسان نیستند.",
    "Your old password was entered incorrectly. Please enter it again.": (
        "رمز عبور فعلی اشتباه است."
    ),
    "Please leave this field blank.": "این فیلد باید خالی بماند.",
}


def translate_error_message(message):
    if not message:
        return message
    text = str(message)
    if text in ENGLISH_TO_PERSIAN:
        return ENGLISH_TO_PERSIAN[text]
    return text


def _merge_messages(field, extra):
    field.error_messages = {**extra, **field.error_messages}


def apply_persian_errors_to_form(form):
    """پیام‌های فارسی را روی فیلدهای یک فرم اعمال می‌کند."""
    for field in form.fields.values():
        if isinstance(field, forms.EmailField):
            _merge_messages(field, EMAIL_FIELD_ERROR_MESSAGES)
        elif isinstance(field, forms.IntegerField):
            _merge_messages(field, INTEGER_FIELD_ERROR_MESSAGES)
        elif isinstance(field, forms.URLField):
            _merge_messages(field, URL_FIELD_ERROR_MESSAGES)
        elif isinstance(field, (forms.DateField, forms.TimeField)):
            _merge_messages(field, DATE_FIELD_ERROR_MESSAGES)
        elif isinstance(field, forms.DateTimeField):
            _merge_messages(field, DATETIME_FIELD_ERROR_MESSAGES)
        elif isinstance(field, (forms.FileField, forms.ImageField)):
            _merge_messages(field, FILE_FIELD_ERROR_MESSAGES)
        else:
            _merge_messages(field, DEFAULT_FIELD_ERROR_MESSAGES)

    if hasattr(form, "error_messages"):
        form.error_messages.update(AUTH_FORM_ERROR_MESSAGES)


def patch_django_forms():
    """همهٔ فرم‌های پروژه به‌صورت خودکار پیام فارسی دریافت می‌کنند."""
    _patch_init(forms.BaseForm, apply_persian_errors_to_form)
    _patch_init(model_forms.BaseModelForm, apply_persian_errors_to_form)


def patch_rest_framework_fields():
    try:
        from rest_framework import serializers
    except ImportError:
        return

    serializers.Field.default_error_messages.update(
        {
            "required": "پر کردن این فیلد الزامی است.",
            "null": "این فیلد نمی‌تواند خالی باشد.",
            "blank": "پر کردن این فیلد الزامی است.",
            "invalid": "مقدار وارد شده معتبر نیست.",
            "invalid_choice": "گزینه انتخاب‌شده معتبر نیست.",
            "max_length": "حداکثر %(max_length)s کاراکتر مجاز است.",
            "min_length": "حداقل %(min_length)s کاراکتر لازم است.",
            "max_value": "مقدار باید حداکثر %(max_value)s باشد.",
            "min_value": "مقدار باید حداقل %(min_value)s باشد.",
            "overflow": "عدد وارد شده بیش از حد بزرگ است.",
            "empty": "حداقل یک مورد انتخاب کنید.",
        }
    )


def _patch_init(base_cls, callback):
    if getattr(base_cls.__init__, "_persian_patched", False):
        return
    original_init = base_cls.__init__

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        callback(self)

    __init__._persian_patched = True
    base_cls.__init__ = __init__

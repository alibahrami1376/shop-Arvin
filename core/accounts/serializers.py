from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from accounts.models import UserType, ensure_user_profile
from accounts.utils import consume_otp, get_valid_otp, sms_otp_enabled
from accounts.validators import validate_iranian_cellphone_number

User = get_user_model()


def _normalize_phone(value: str) -> str:
    s = str(value).strip().replace(" ", "")
    persian = "۰۱۲۳۴۵۶۷۸۹"
    latin = "0123456789"
    return s.translate(str.maketrans(persian, latin))


class UserSerializer(serializers.ModelSerializer):
    """اطلاعات کاربر بدون رمز."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "phone_verified",
            "is_verified",
            "type",
        )
        read_only_fields = fields


class RegisterEmailSerializer(serializers.Serializer):
    """منسوخ: ثبت‌نام فقط با شماره موبایل."""

    email = serializers.EmailField(label="ایمیل")
    password = serializers.CharField(write_only=True, min_length=8, label="رمز عبور")
    password2 = serializers.CharField(write_only=True, label="تکرار رمز عبور")

    def validate(self, attrs):
        raise serializers.ValidationError(
            "ثبت‌نام فقط با شماره موبایل انجام می‌شود. از /api/accounts/register/phone/ استفاده کنید."
        )


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, label="شماره موبایل")

    def validate_phone_number(self, value):
        phone = _normalize_phone(value)
        validate_iranian_cellphone_number(phone)
        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("کاربری با این شماره موبایل از قبل وجود دارد.")
        return phone


class RegisterPhoneSerializer(serializers.Serializer):
    """ثبت‌نام مستقیم با موبایل وقتی OTP در پنل ادمین غیرفعال است."""

    phone_number = serializers.CharField(max_length=20, label="شماره موبایل")
    password = serializers.CharField(write_only=True, min_length=8, label="رمز عبور")
    password2 = serializers.CharField(write_only=True, label="تکرار رمز عبور")
    first_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_phone_number(self, value):
        phone = _normalize_phone(value)
        validate_iranian_cellphone_number(phone)
        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("کاربری با این شماره موبایل از قبل وجود دارد.")
        return phone

    def validate(self, attrs):
        if sms_otp_enabled():
            raise serializers.ValidationError(
                "ثبت‌نام بدون کد تأیید فقط وقتی OTP غیرفعال است امکان‌پذیر است."
            )
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "رمز عبور و تکرار آن یکسان نیستند."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        try:
            user = User.objects.create_customer(
                validated_data["phone_number"],
                validated_data["password"],
                is_verified=False,
                phone_verified=True,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        profile = ensure_user_profile(user)
        profile.first_name = validated_data.get("first_name", "")
        profile.last_name = validated_data.get("last_name", "")
        profile.save(update_fields=["first_name", "last_name", "updated_date"])
        return user


class VerifyOTPRegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6, min_length=6)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_phone_number(self, value):
        phone = _normalize_phone(value)
        validate_iranian_cellphone_number(phone)
        return phone

    def validate(self, attrs):
        if not sms_otp_enabled():
            raise serializers.ValidationError(
                "تأیید با پیامک غیرفعال است. از ثبت‌نام مستقیم با موبایل استفاده کنید."
            )
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "رمز عبور و تکرار آن یکسان نیستند."})
        validate_password(attrs["password"])
        phone = attrs["phone_number"]
        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError(
                {"phone_number": "کاربری با این شماره از قبل وجود دارد."}
            )
        return attrs

    def create(self, validated_data):
        try:
            user = User.objects.create_customer(
                validated_data["phone_number"],
                validated_data["password"],
                is_verified=False,
                otp_code=validated_data["code"],
            )
        except ValueError as exc:
            raise serializers.ValidationError({"code": str(exc)}) from exc
        profile = ensure_user_profile(user)
        profile.first_name = validated_data.get("first_name", "")
        profile.last_name = validated_data.get("last_name", "")
        profile.save(update_fields=["first_name", "last_name", "updated_date"])
        return user


class LoginSerializer(serializers.Serializer):
    """username می‌تواند ایمیل یا شماره موبایل باشد."""

    username = serializers.CharField(label="ایمیل یا موبایل")
    password = serializers.CharField(write_only=True, label="رمز عبور")

    def validate(self, attrs):
        request = self.context.get("request")
        username = attrs["username"].strip()
        password = attrs["password"]
        user = authenticate(request=request, username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                "ایمیل/موبایل یا رمز عبور اشتباه است."
            )
        if not user.is_active:
            raise serializers.ValidationError("این حساب غیرفعال است.")
        attrs["user"] = user
        return attrs


class VerifyPhoneOTPSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6, label="کد تأیید")

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        if not user.phone_number:
            raise serializers.ValidationError("ابتدا شماره موبایل را در پروفایل ثبت کنید.")
        if user.phone_verified:
            raise serializers.ValidationError("موبایل شما قبلاً تأیید شده است.")
        if not sms_otp_enabled():
            raise serializers.ValidationError(
                "تأیید با پیامک در پنل مدیریت غیرفعال است."
            )
        try:
            attrs["_otp"] = get_valid_otp(user.phone_number, attrs["code"])
        except ValidationError as exc:
            raise serializers.ValidationError({"code": exc.message}) from exc
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        consume_otp(self.validated_data["_otp"])
        user.phone_verified = True
        user.save(update_fields=["phone_verified"])
        return user

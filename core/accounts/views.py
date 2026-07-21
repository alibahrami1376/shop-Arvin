import logging

from django.contrib import messages
from django.contrib.auth import get_user_model,authenticate, login, views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.forms import AuthenticationForm, UserRegistrationForm
from accounts.models import OTPCode, SMSSettings, UserType, ensure_user_profile

REGISTER_OTP_SESSION_EXPIRES = "register_otp_expires_at"
REGISTER_OTP_SESSION_PHONE = "register_otp_phone"
from accounts.serializers import (
    LoginSerializer,
    RegisterEmailSerializer,
    RegisterPhoneSerializer,
    SendOTPSerializer,
    UserSerializer,
    VerifyOTPRegisterSerializer,
    VerifyPhoneOTPSerializer,
)
from accounts.utils import send_otp_via_kavenegar, sms_otp_enabled

User = get_user_model()
logger = logging.getLogger(__name__)

# پیام زمانی که ارسال پیامک از پنل ادمین خاموش باشد
SMS_DISABLED_DETAIL = (
    "ارسال پیامک از پنل مدیریت غیرفعال است. برای فعال‌سازی به «تنظیمات پیامک (OTP)» در داشبورد ادمین مراجعه کنید."
)


def _profile_edit_redirect(request):
    """بازگشت به صفحه ویرایش پروفایل (مشتری یا ادمین)."""
    if getattr(request.user, "type", None) in (
        UserType.admin.value,
        UserType.superuser.value,
    ) or request.user.is_staff:
        return reverse_lazy("dashboard:admin:profile-edit")
    return reverse_lazy("dashboard:customer:profile-edit")


def _jwt_payload(user):
    """توکن‌های JWT برای پاسخ API."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["require_otp"] = sms_otp_enabled()
        kwargs["otp_expires_at"] = self.request.session.get(REGISTER_OTP_SESSION_EXPIRES)
        kwargs["otp_session_phone"] = self.request.session.get(REGISTER_OTP_SESSION_PHONE)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sms_otp_enabled"] = sms_otp_enabled()
        context["otp_validity_seconds"] = OTPCode.validity_seconds()
        context["otp_expires_at"] = self.request.session.get(REGISTER_OTP_SESSION_EXPIRES)
        form = context.get("form")
        sms_on = context["sms_otp_enabled"]
        if form:
            method = (
                (form.data.get("register_method") or "").strip()
                if form.is_bound
                else ""
            )
            if not sms_on:
                method = UserRegistrationForm.REGISTER_EMAIL
            elif method not in (
                UserRegistrationForm.REGISTER_EMAIL,
                UserRegistrationForm.REGISTER_PHONE,
            ):
                if self.request.session.get(REGISTER_OTP_SESSION_PHONE):
                    method = UserRegistrationForm.REGISTER_PHONE
                elif form.errors.get("phone_number") or (
                    form.data.get("phone_number") or ""
                ).strip():
                    method = UserRegistrationForm.REGISTER_PHONE
                elif form.errors.get("email") or (form.data.get("email") or "").strip():
                    method = UserRegistrationForm.REGISTER_EMAIL
                else:
                    method = UserRegistrationForm.REGISTER_EMAIL
            context["register_method"] = method
        return context

    def form_valid(self, form):
        phone = form.cleaned_data.get("phone_number")
        otp_code = (form.cleaned_data.get("otp_code") or "").strip() or None
        if not phone:
            otp_code = None
        try:
            user = User.objects.create_customer(
                phone_number=phone,
                password=form.cleaned_data["password1"],       
                email=form.cleaned_data.get("email"),
                is_verified=False,
                otp_code=otp_code,
            )
        except ValueError as exc:
            if sms_otp_enabled() and phone:
                form.add_error("otp_code", str(exc))
            else:
                form.add_error(None, str(exc))
            return self.form_invalid(form)
        profile = ensure_user_profile(user)
        profile.first_name = form.cleaned_data.get("first_name", "")
        profile.last_name = form.cleaned_data.get("last_name", "")
        profile.save(update_fields=["first_name", "last_name", "updated_date"])
        self.request.session.pop(REGISTER_OTP_SESSION_EXPIRES, None)
        self.request.session.pop(REGISTER_OTP_SESSION_PHONE, None)
        login(self.request, user, backend="accounts.backends.EmailOrPhoneBackend",)
        return redirect(self.get_success_url())


@method_decorator(csrf_protect, name="dispatch")
class WebRegisterSendOTPView(View):
    """ارسال کد OTP هنگام ثبت‌نام (فقط وقتی OTP در پنل ادمین فعال است)."""

    def post(self, request, *args, **kwargs):
        if not sms_otp_enabled():
            messages.error(request, SMS_DISABLED_DETAIL)
            return redirect("accounts:register")

        raw_phone = (request.POST.get("phone_number") or "").strip()
        if not raw_phone:
            messages.error(request, "شماره موبایل را وارد کنید.")
            return redirect("accounts:register")

        try:
            phone = User.objects.normalize_phone(raw_phone)
        except Exception:
            messages.error(request, "شماره موبایل معتبر نیست.")
            return redirect("accounts:register")

        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, "این شماره موبایل قبلاً ثبت شده است.")
            return redirect("accounts:register")

        otp = OTPCode(mobile=phone)
        otp.save()
        ok, err = send_otp_via_kavenegar(phone, otp.code)
        if ok:
            from django.utils import timezone

            expires = timezone.now().timestamp() + OTPCode.validity_seconds()
            request.session[REGISTER_OTP_SESSION_EXPIRES] = expires
            request.session[REGISTER_OTP_SESSION_PHONE] = phone
            request.session.modified = True
            messages.success(request, "کد تأیید به شماره شما ارسال شد.")
        else:
            messages.error(request, err or "ارسال پیامک با خطا مواجه شد.")
        return redirect("accounts:register")


# ——— API (DRF + SimpleJWT) ———


class RegisterEmailView(APIView):
    """ثبت‌نام با ایمیل و رمز؛ بدون OTP ایمیل."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {"user": UserSerializer(user).data, "tokens": _jwt_payload(user)}
        return Response(data, status=status.HTTP_201_CREATED)


class RegisterPhoneView(APIView):
    """ثبت‌نام مستقیم با موبایل (بدون OTP) وقتی پیامک در پنل ادمین غیرفعال است."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {"user": UserSerializer(user).data, "tokens": _jwt_payload(user)}
        return Response(data, status=status.HTTP_201_CREATED)


class SendOTPView(APIView):
    """ارسال OTP برای ثبت‌نام با موبایل."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if not sms_otp_enabled():
            return Response(
                {"detail": SMS_DISABLED_DETAIL},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]
        otp = OTPCode(mobile=phone)
        otp.save()
        ok, err = send_otp_via_kavenegar(phone, otp.code)
        if not ok:
            return Response(
                {"detail": err or "ارسال پیامک با خطا مواجه شد."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"message": "کد تأیید به شماره شما ارسال شد."})


class VerifyOTPRegisterView(APIView):
    """تأیید OTP و ایجاد کاربر با موبایل تأییدشده."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {"user": UserSerializer(user).data, "tokens": _jwt_payload(user)}
        return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """ورود با ایمیل یا شماره موبایل + رمز."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        data = {"user": UserSerializer(user).data, "tokens": _jwt_payload(user)}
        return Response(data)


class SendVerifyPhoneOTPView(APIView):
    """ارسال OTP تأیید موبایل برای کاربر لاگین‌شده (JWT یا سشن در DRF اگر تنظیم شود)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.phone_number:
            return Response(
                {"detail": "ابتدا شماره موبایل را در پروفایل ثبت کنید."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.phone_verified:
            return Response(
                {"detail": "موبایل شما قبلاً تأیید شده است."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not SMSSettings.get_solo().sms_enabled:
            return Response(
                {"detail": SMS_DISABLED_DETAIL},
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp = OTPCode(mobile=user.phone_number)
        otp.save()
        ok, err = send_otp_via_kavenegar(user.phone_number, otp.code)
        if not ok:
            return Response(
                {"detail": err or "ارسال پیامک با خطا مواجه شد."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"message": "کد تأیید به شماره شما ارسال شد."})


class VerifyPhoneOTPView(APIView):
    """تأیید کد و علامت‌گذاری موبایل به‌عنوان تأییدشده."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = VerifyPhoneOTPSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "شماره موبایل با موفقیت تأیید شد."})


# ——— وب: تأیید موبایل با سشن (برای کاربران فقط وب‌سایت) ———


@method_decorator(csrf_protect, name="dispatch")
class WebSendVerifyPhoneOTPView(LoginRequiredMixin, View):
    """ارسال کد OTP تأیید موبایل (فرم POST از داشبورد)."""

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.phone_number:
            messages.error(request, "ابتدا شماره موبایل را در پروفایل ذخیره کنید.")
        elif user.phone_verified:
            messages.info(request, "موبایل شما قبلاً تأیید شده است.")
        elif not SMSSettings.get_solo().sms_enabled:
            messages.error(request, SMS_DISABLED_DETAIL)
        else:
            otp = OTPCode(mobile=user.phone_number)
            otp.save()
            ok, err = send_otp_via_kavenegar(user.phone_number, otp.code)
            if ok:
                messages.success(request, "کد تأیید به شماره شما ارسال شد.")
            else:
                messages.error(request, err or "ارسال پیامک با خطا مواجه شد.")
        return redirect(_profile_edit_redirect(request))


@method_decorator(csrf_protect, name="dispatch")
class WebVerifyPhoneOTPView(LoginRequiredMixin, View):
    """تأیید کد OTP از فرم وب."""

    def post(self, request, *args, **kwargs):
        serializer = VerifyPhoneOTPSerializer(
            data={"code": request.POST.get("code", "")},
            context={"request": request},
        )
        if not serializer.is_valid():
            for field, errs in serializer.errors.items():
                for err in errs if isinstance(errs, list) else [errs]:
                    messages.error(request, str(err))
            return redirect(_profile_edit_redirect(request))
        serializer.save()
        messages.success(request, "شماره موبایل با موفقیت تأیید شد.")
        return redirect(_profile_edit_redirect(request))

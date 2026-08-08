from django.contrib import messages
from django.contrib.auth import get_user_model, login, views as auth_views
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView

from accounts.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserRegistrationForm,
)
from accounts.models import OTPCode, ensure_user_profile
from accounts.services import OTPService
from accounts.utils import consume_otp

User = get_user_model()

AUTH_BACKEND = "accounts.backends.EmailOrPhoneBackend"
REGISTER_OTP_SESSION_EXPIRES = "register_otp_expires_at"
REGISTER_OTP_SESSION_PHONE = "register_otp_phone"
RESET_OTP_SESSION_EXPIRES = "reset_otp_expires_at"
RESET_OTP_SESSION_PHONE = "reset_otp_phone"


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

    def get_initial(self):
        initial = super().get_initial()
        session_phone = self.request.session.get(REGISTER_OTP_SESSION_PHONE)
        if session_phone:
            initial["register_method"] = UserRegistrationForm.REGISTER_PHONE
            initial["phone_number"] = session_phone
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["otp_expires_at"] = self.request.session.get(REGISTER_OTP_SESSION_EXPIRES)
        kwargs["otp_session_phone"] = self.request.session.get(REGISTER_OTP_SESSION_PHONE)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form")
        session_phone = self.request.session.get(REGISTER_OTP_SESSION_PHONE)
        method = UserRegistrationForm.REGISTER_EMAIL

        if form and form.is_bound:
            raw = (form.data.get("register_method") or "").strip()
            if raw in (
                UserRegistrationForm.REGISTER_EMAIL,
                UserRegistrationForm.REGISTER_PHONE,
            ):
                method = raw
            elif form.errors.get("phone_number") or form.errors.get("otp_code") or (
                form.data.get("phone_number") or ""
            ).strip():
                method = UserRegistrationForm.REGISTER_PHONE
            elif form.errors.get("email") or (form.data.get("email") or "").strip():
                method = UserRegistrationForm.REGISTER_EMAIL
        elif session_phone:
            method = UserRegistrationForm.REGISTER_PHONE

        context["register_method"] = method
        context["otp_validity_seconds"] = OTPCode.validity_seconds()
        context["otp_expires_at"] = self.request.session.get(REGISTER_OTP_SESSION_EXPIRES)
        context["otp_session_phone"] = session_phone or ""
        return context

    def form_valid(self, form):
        otp = form.cleaned_data.get("_otp")
        phone = form.cleaned_data.get("phone_number")
        is_verified = bool(otp and phone)
        try:
            user = User.objects.create_customer(
                password=form.cleaned_data["password1"],
                email=form.cleaned_data.get("email"),
                phone_number=phone,
                is_verified=is_verified,
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        if otp is not None:
            consume_otp(otp, user=user)
        profile = ensure_user_profile(user)
        profile.first_name = form.cleaned_data.get("first_name", "")
        profile.last_name = form.cleaned_data.get("last_name", "")
        profile.save(update_fields=["first_name", "last_name", "updated_date"])
        self.request.session.pop(REGISTER_OTP_SESSION_EXPIRES, None)
        self.request.session.pop(REGISTER_OTP_SESSION_PHONE, None)
        login(self.request, user, backend=AUTH_BACKEND)
        return redirect(self.get_success_url())


@method_decorator(csrf_protect, name="dispatch")
class WebRegisterSendOTPView(View):
    """ارسال کد OTP هنگام ثبت‌نام با موبایل (JSON برای AJAX یا ریدایرکت)."""

    def _wants_json(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return True
        accept = request.headers.get("Accept", "")
        return "application/json" in accept

    def _error(self, request, message, status=400):
        if self._wants_json(request):
            return JsonResponse({"ok": False, "detail": message}, status=status)
        messages.error(request, message)
        return redirect("accounts:register")

    def _success(self, request, phone, expires):
        if self._wants_json(request):
            return JsonResponse(
                {
                    "ok": True,
                    "detail": "کد تأیید به شماره شما ارسال شد.",
                    "phone_number": phone,
                    "otp_expires_at": expires,
                    "otp_validity_seconds": OTPCode.validity_seconds(),
                }
            )
        messages.success(request, "کد تأیید به شماره شما ارسال شد.")
        return redirect("accounts:register")

    def post(self, request, *args, **kwargs):
        raw_phone = (request.POST.get("phone_number") or "").strip()
        if not raw_phone:
            return self._error(request, "شماره موبایل را وارد کنید.")

        try:
            phone = User.objects.normalize_phone(raw_phone)
        except Exception:
            return self._error(request, "شماره موبایل معتبر نیست.")

        if User.objects.filter(phone_number=phone).exists():
            return self._error(request, "این شماره موبایل قبلاً ثبت شده است.")

        otp, err = OTPService().create_and_send(phone)
        if otp is None:
            return self._error(
                request,
                err or "ارسال پیامک با خطا مواجه شد.",
                status=503,
            )

        from django.utils import timezone

        expires = timezone.now().timestamp() + OTPCode.validity_seconds()
        request.session[REGISTER_OTP_SESSION_EXPIRES] = expires
        request.session[REGISTER_OTP_SESSION_PHONE] = phone
        request.session.modified = True
        return self._success(request, phone, expires)


class PasswordResetView(FormView):
    """بازیابی رمز عبور با موبایل + OTP."""

    template_name = "accounts/password_reset.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        session_phone = self.request.session.get(RESET_OTP_SESSION_PHONE)
        if session_phone:
            initial["phone_number"] = session_phone
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["otp_expires_at"] = self.request.session.get(RESET_OTP_SESSION_EXPIRES)
        kwargs["otp_session_phone"] = self.request.session.get(RESET_OTP_SESSION_PHONE)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_phone = self.request.session.get(RESET_OTP_SESSION_PHONE)
        context["otp_validity_seconds"] = OTPCode.validity_seconds()
        context["otp_expires_at"] = self.request.session.get(RESET_OTP_SESSION_EXPIRES)
        context["otp_session_phone"] = session_phone or ""
        return context

    def form_valid(self, form):
        user = form.cleaned_data["_user"]
        otp = form.cleaned_data["_otp"]
        user.set_password(form.cleaned_data["password1"])
        user.save(update_fields=["password"])
        consume_otp(otp, user=user)
        self.request.session.pop(RESET_OTP_SESSION_EXPIRES, None)
        self.request.session.pop(RESET_OTP_SESSION_PHONE, None)
        messages.success(
            self.request,
            "رمز عبور با موفقیت تغییر کرد. با رمز جدید وارد شوید.",
        )
        return redirect(self.get_success_url())


@method_decorator(csrf_protect, name="dispatch")
class PasswordResetSendOTPView(View):
    """ارسال OTP برای بازیابی رمز عبور."""

    def _wants_json(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return True
        accept = request.headers.get("Accept", "")
        return "application/json" in accept

    def _error(self, request, message, status=400):
        if self._wants_json(request):
            return JsonResponse({"ok": False, "detail": message}, status=status)
        messages.error(request, message)
        return redirect("accounts:password-reset")

    def _success(self, request, phone, expires):
        if self._wants_json(request):
            return JsonResponse(
                {
                    "ok": True,
                    "detail": "کد تأیید به شماره شما ارسال شد.",
                    "phone_number": phone,
                    "otp_expires_at": expires,
                    "otp_validity_seconds": OTPCode.validity_seconds(),
                }
            )
        messages.success(request, "کد تأیید به شماره شما ارسال شد.")
        return redirect("accounts:password-reset")

    def post(self, request, *args, **kwargs):
        raw_phone = (request.POST.get("phone_number") or "").strip()
        if not raw_phone:
            return self._error(request, "شماره موبایل را وارد کنید.")

        try:
            phone = User.objects.normalize_phone(raw_phone)
        except Exception:
            return self._error(request, "شماره موبایل معتبر نیست.")

        user = User.objects.filter(phone_number=phone).first()
        if user is None:
            return self._error(request, "حسابی با این شماره موبایل یافت نشد.")

        otp, err = OTPService().create_and_send(phone, user=user)
        if otp is None:
            return self._error(
                request,
                err or "ارسال پیامک با خطا مواجه شد.",
                status=503,
            )

        from django.utils import timezone

        expires = timezone.now().timestamp() + OTPCode.validity_seconds()
        request.session[RESET_OTP_SESSION_EXPIRES] = expires
        request.session[RESET_OTP_SESSION_PHONE] = phone
        request.session.modified = True
        return self._success(request, phone, expires)

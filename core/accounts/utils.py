"""توابع کمکی احراز هویت — برای سازگاری با فرم‌ها."""

from django.utils.http import url_has_allowed_host_and_scheme

from accounts.services.otp import OTPService

_otp_service = OTPService()

AUTH_NEXT_SESSION_KEY = "auth_next_url"


def get_valid_otp(mobile: str, code: str):
    return _otp_service.get_valid(mobile, code)


def consume_otp(otp, user=None) -> None:
    _otp_service.consume(otp, user=user)


def _is_safe_auth_next(request, redirect_to: str) -> bool:
    return bool(
        redirect_to
        and url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
    )


def get_safe_auth_next(request, default=None):
    """امن‌ترین next از POST/GET/session برای بازگشت بعد از ورود یا ثبت‌نام."""
    for redirect_to in (
        (request.POST.get("next") or "").strip(),
        (request.GET.get("next") or "").strip(),
        (request.session.get(AUTH_NEXT_SESSION_KEY) or "").strip(),
    ):
        if _is_safe_auth_next(request, redirect_to):
            return redirect_to
    return default


def stash_auth_next(request) -> str:
    """اگر next معتبر در درخواست باشد در session نگه می‌دارد."""
    fresh = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if _is_safe_auth_next(request, fresh):
        request.session[AUTH_NEXT_SESSION_KEY] = fresh
        request.session.modified = True
        return fresh
    stored = (request.session.get(AUTH_NEXT_SESSION_KEY) or "").strip()
    return stored if _is_safe_auth_next(request, stored) else ""


def pop_auth_next(request, default=None):
    redirect_to = get_safe_auth_next(request, default=None)
    request.session.pop(AUTH_NEXT_SESSION_KEY, None)
    return redirect_to or default

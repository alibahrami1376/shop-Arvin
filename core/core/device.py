"""Device detection helpers (django-user-agents on request)."""


def _ua_is_phone(request) -> bool:
    ua = getattr(request, "user_agent", None)
    if ua is None:
        return False
    return bool(ua.is_mobile) and not bool(ua.is_tablet)


def is_mobile_site(request) -> bool:
    """True for phones only — tablets and desktop use the desktop layout.

    Priority:
    1. Explicit ``?site=`` (legacy/manual override only; layout-sync uses cookie)
    2. Real phone signals (User-Agent / Client Hints) — beat a stale cookie
    3. ``site_layout`` cookie — for desktop UA with a narrow viewport
    """
    forced = request.GET.get("site")
    if forced == "mobile":
        return True
    if forced == "desktop":
        return False

    # Phone UA / Client Hints win over site_layout=desktop (DevTools + real phones)
    if _ua_is_phone(request):
        return True
    if request.META.get("HTTP_SEC_CH_UA_MOBILE") == "?1":
        return True

    cookie = request.COOKIES.get("site_layout")
    if cookie == "mobile":
        return True
    if cookie == "desktop":
        return False

    return False


def get_device_type(request) -> str:
    return "mobile" if is_mobile_site(request) else "desktop"


def filter_queryset_for_device(queryset, request, field_name="display_target"):
    """Keep rows marked for this device or for all devices."""
    if is_mobile_site(request):
        allowed = ("all", "mobile")
    else:
        allowed = ("all", "desktop")
    return queryset.filter(**{f"{field_name}__in": allowed})

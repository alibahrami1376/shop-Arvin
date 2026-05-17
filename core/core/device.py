"""Device detection helpers (django-user-agents on request)."""


def is_mobile_site(request) -> bool:
    """True for phones and tablets — mobile layout."""
    forced = request.GET.get("site") or request.COOKIES.get("site_layout")
    if forced == "mobile":
        return True
    if forced == "desktop":
        return False

    # Client Hints (Chrome/Android)
    if request.META.get("HTTP_SEC_CH_UA_MOBILE") == "?1":
        return True

    ua = getattr(request, "user_agent", None)
    if ua is None:
        return False
    return bool(ua.is_mobile or ua.is_tablet)


def get_device_type(request) -> str:
    return "mobile" if is_mobile_site(request) else "desktop"


def filter_queryset_for_device(queryset, request, field_name="display_target"):
    """Keep rows marked for this device or for all devices."""
    if is_mobile_site(request):
        allowed = ("all", "mobile")
    else:
        allowed = ("all", "desktop")
    return queryset.filter(**{f"{field_name}__in": allowed})

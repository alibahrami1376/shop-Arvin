"""Resolve desktop vs mobile template paths for frontend pages."""

from typing import Optional

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from core.device import is_mobile_site

MOBILE_TEMPLATE_SUFFIX = "-mobile"


def mobile_template_for(template_name: str) -> str:
    if template_name.endswith(".html"):
        return template_name[: -len(".html")] + f"{MOBILE_TEMPLATE_SUFFIX}.html"
    return f"{template_name}{MOBILE_TEMPLATE_SUFFIX}"


def template_exists(template_name: str) -> bool:
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False


def resolve_device_template(
    request,
    template_name: str,
    *,
    mobile_template_name: Optional[str] = None,
    desktop_template_name: Optional[str] = None,
) -> str:
    """Pick mobile or desktop template for the current request."""
    if is_mobile_site(request):
        mobile = mobile_template_name or mobile_template_for(template_name)
        if template_exists(mobile):
            return mobile
        return template_name
    return desktop_template_name or template_name

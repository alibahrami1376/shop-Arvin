from django import template

from core.device import get_device_type, is_mobile_site

register = template.Library()


@register.simple_tag(takes_context=True)
def device_type(context):
    request = context.get("request")
    if request is None:
        return "desktop"
    return get_device_type(request)


@register.filter
def mobile_site(request):
    return is_mobile_site(request)


@register.filter
def desktop_site(request):
    return not is_mobile_site(request)

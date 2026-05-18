from core.device import get_device_type, is_mobile_site


def device(request):
    mobile = is_mobile_site(request)
    return {
        "device_type": get_device_type(request),
        "is_mobile_site": mobile,
        "is_desktop_site": not mobile,
        # Prefer explicit base in templates; kept for legacy {% extends base_template %}
        "base_template": "base-mobile.html" if mobile else "base-desktop.html",
        "base_mobile_template": "base-mobile.html",
        "base_desktop_template": "base-desktop.html",
    }

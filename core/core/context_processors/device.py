from core.device import get_device_type, is_mobile_site


def device(request):
    mobile = is_mobile_site(request)
    return {
        "device_type": get_device_type(request),
        "is_mobile_site": mobile,
        "is_desktop_site": not mobile,
        "base_template": "base-mobile.html" if mobile else "base-desktop.html",
        "base_mobile_template": "base-mobile.html",
        "base_desktop_template": "base-desktop.html",
        "dashboard_customer_base_template": (
            "dashboard/customer/base-mobile.html"
            if mobile
            else "dashboard/customer/base-desktop.html"
        ),
        "dashboard_admin_base_template": (
            "dashboard/admin/base-mobile.html"
            if mobile
            else "dashboard/admin/base-desktop.html"
        ),
    }

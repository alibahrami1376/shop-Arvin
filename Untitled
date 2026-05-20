from core.device import is_mobile_site
from core.device_templates import resolve_device_template


class DeviceTemplateMixin:
    """
    Use separate templates for mobile and desktop frontend.

    Convention: ``shop/product-grid.html`` (desktop) and ``shop/product-grid-mobile.html`` (mobile).
    Override with ``mobile_template_name`` / ``desktop_template_name`` when needed.
    """

    mobile_template_name = None
    desktop_template_name = None

    def get_template_names(self):
        names = super().get_template_names()
        if not names:
            return names
        return [
            resolve_device_template(
                self.request,
                names[0],
                mobile_template_name=self.mobile_template_name,
                desktop_template_name=self.desktop_template_name,
            )
        ]

    def get_template_name(self):
        """For single-template views (e.g. LoginView)."""
        name = super().get_template_name()
        return resolve_device_template(
            self.request,
            name,
            mobile_template_name=self.mobile_template_name,
            desktop_template_name=self.desktop_template_name,
        )

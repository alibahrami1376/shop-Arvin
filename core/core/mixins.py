from core.device import is_mobile_site


class DeviceTemplateMixin:
    """Pick mobile or desktop template_name when the matching file is set."""

    mobile_template_name = None
    desktop_template_name = None

    def get_template_names(self):
        if is_mobile_site(self.request) and self.mobile_template_name:
            return [self.mobile_template_name]
        if not is_mobile_site(self.request) and self.desktop_template_name:
            return [self.desktop_template_name]
        return super().get_template_names()

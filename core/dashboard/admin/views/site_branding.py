from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from dashboard.admin.forms import SiteBrandingSettingsForm
from dashboard.permissions import HasAdminAccessPermission
from website.logo_validation import SITE_LOGO_HEIGHT, SITE_LOGO_WIDTH
from website.models import SiteBrandingSettings


class AdminSiteBrandingSettingsView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = SiteBrandingSettings
    form_class = SiteBrandingSettingsForm
    template_name = "dashboard/admin/branding/site-branding-settings.html"
    success_url = reverse_lazy("dashboard:admin:site-branding-settings")
    success_message = "لوگوی سایت با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        return SiteBrandingSettings.get_solo()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["logo_width"] = SITE_LOGO_WIDTH
        context["logo_height"] = SITE_LOGO_HEIGHT
        return context

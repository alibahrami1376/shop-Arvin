from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from dashboard.admin.forms import SiteWideSocialSettingsForm
from dashboard.permissions import HasAdminAccessPermission
from website.models import SiteWideSocialSettings


class AdminSiteWideSocialSettingsView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = SiteWideSocialSettings
    form_class = SiteWideSocialSettingsForm
    template_name = "dashboard/admin/social/site-wide-social-settings.html"
    success_url = reverse_lazy("dashboard:admin:site-wide-social-settings")
    success_message = "لینک‌های شبکه‌های اجتماعی سایت با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        return SiteWideSocialSettings.get_solo()

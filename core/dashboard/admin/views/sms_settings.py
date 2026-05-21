from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.models import SMSSettings
from dashboard.admin.forms import SMSSettingsForm
from dashboard.permissions import HasAdminAccessPermission


class AdminSMSSettingsView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = SMSSettings
    form_class = SMSSettingsForm
    template_name = "dashboard/admin/accounts/sms-settings.html"
    success_url = reverse_lazy("dashboard:admin:sms-settings")
    success_message = "تنظیمات پیامک (OTP) با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        return SMSSettings.get_solo()

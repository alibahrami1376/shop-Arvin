from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from dashboard.admin.forms import ContactPageSettingsForm
from dashboard.permissions import HasAdminAccessPermission
from website.models import ContactPageSettings


class AdminContactPageSettingsView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = ContactPageSettings
    form_class = ContactPageSettingsForm
    template_name = "dashboard/admin/contact/contact-settings.html"
    success_url = reverse_lazy("dashboard:admin:contact-settings")
    success_message = "تنظیمات تماس با ما با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        return ContactPageSettings.get_solo()

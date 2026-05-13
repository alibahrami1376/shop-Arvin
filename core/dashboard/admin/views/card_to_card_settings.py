from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from dashboard.admin.forms import CardToCardSettingsForm
from dashboard.permissions import HasAdminAccessPermission
from payment.models import CardToCardSettings


class AdminCardToCardSettingsView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = CardToCardSettings
    form_class = CardToCardSettingsForm
    template_name = "dashboard/admin/payment/card-to-card-settings.html"
    success_url = reverse_lazy("dashboard:admin:card-to-card-settings")
    success_message = "تنظیمات کارت به کارت با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        return CardToCardSettings.get_solo()

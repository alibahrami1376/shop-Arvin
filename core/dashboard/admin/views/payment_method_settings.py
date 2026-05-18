from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from dashboard.admin.forms import PaymentMethodSettingsForm
from dashboard.permissions import HasAdminAccessPermission
from payment.models import PaymentMethodSettings
from dashboard.mixins import DashboardDeviceTemplateMixin


class AdminPaymentMethodSettingsView(DashboardDeviceTemplateMixin, LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    model = PaymentMethodSettings
    form_class = PaymentMethodSettingsForm
    template_name = "dashboard/admin/payment/payment-method-settings.html"
    success_url = reverse_lazy("dashboard:admin:payment-method-settings")
    success_message = "تنظیمات روش‌های پرداخت با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        return PaymentMethodSettings.get_solo()

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from dashboard.admin.forms import CheckoutPricingSettingsForm
from dashboard.permissions import HasAdminAccessPermission
from order.models import CheckoutPricingSettings


class AdminCheckoutPricingSettingsView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = CheckoutPricingSettings
    form_class = CheckoutPricingSettingsForm
    template_name = "dashboard/admin/order/checkout-pricing-settings.html"
    success_url = reverse_lazy("dashboard:admin:checkout-pricing-settings")
    success_message = "تنظیمات هزینه ارسال و مالیات ذخیره شد."

    def get_object(self, queryset=None):
        return CheckoutPricingSettings.get_solo()

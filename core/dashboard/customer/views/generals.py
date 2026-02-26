from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasCustomerAccessPermission
from order.models import OrderModel, OrderStatusType
from order.models import UserAddressModel
from shop.models import WishlistProductModel


class CustomerDashboardHomeView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "dashboard/customer/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        orders = OrderModel.objects.filter(user=user)
        context["orders_count"] = orders.count()
        context["orders_success_count"] = orders.filter(status=OrderStatusType.success.value).count()
        context["recent_orders"] = orders[:5]
        context["wishlist_count"] = WishlistProductModel.objects.filter(user=user).count()
        context["addresses_count"] = UserAddressModel.objects.filter(user=user).count()
        return context

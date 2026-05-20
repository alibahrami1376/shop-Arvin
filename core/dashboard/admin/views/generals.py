from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasAdminAccessPermission
from accounts.models import User, UserType
from order.models import OrderModel, OrderStatusType
from shop.models import ProductModel
from website.models import ContactModel
from review.models import ReviewModel


class AdminDashboardHomeView(LoginRequiredMixin, HasAdminAccessPermission, TemplateView):
    template_name = "dashboard/admin/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders_count"] = OrderModel.objects.count()
        context["orders_success_count"] = OrderModel.objects.filter(status=OrderStatusType.success.value).count()
        context["orders_pending_count"] = OrderModel.objects.filter(status=OrderStatusType.pending.value).count()
        context["users_count"] = User.objects.filter(type=UserType.customer.value).count()
        context["products_count"] = ProductModel.objects.count()
        context["contacts_count"] = ContactModel.objects.count()
        context["reviews_count"] = ReviewModel.objects.count()
        context["recent_orders"] = OrderModel.objects.select_related("user").order_by("-created_date")[:8]
        return context

from django.contrib import messages
from django.core.exceptions import FieldError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View

from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.admin.forms import AdminOrderStatusForm
from dashboard.permissions import HasAdminAccessPermission
from order.models import OrderModel, OrderStatusType


class AdminOrderListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/orders/order-list.html"
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size',self.paginate_by)

    def get_queryset(self):
        queryset = OrderModel.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(id__icontains=search_q)
        if status := self.request.GET.get("status"):
            queryset = queryset.filter(status=status)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()  
        context["status_types"] = OrderStatusType.choices
        return context
    
class AdminOrderDetailView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/orders/order-detail.html"

    def get_queryset(self):
        return OrderModel.objects.select_related("user", "user__user_profile").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_form"] = AdminOrderStatusForm(instance=self.object)
        return context


class AdminOrderChangeStatusView(LoginRequiredMixin, HasAdminAccessPermission, View):
    http_method_names = ["post"]

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(OrderModel, pk=pk)
        form = AdminOrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "وضعیت سفارش به‌روزرسانی شد.")
        else:
            messages.error(
                request,
                "تغییر وضعیت انجام نشد. دوباره تلاش کنید.",
            )
        return redirect(reverse_lazy("dashboard:admin:order-detail", kwargs={"pk": pk}))


class AdminOrderInvoiceView(LoginRequiredMixin, HasAdminAccessPermission, DetailView):
    template_name = "dashboard/admin/orders/order-invoice.html"

    def get_queryset(self):
        return OrderModel.objects.filter(status=OrderStatusType.success.value)

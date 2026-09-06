from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.views.generic import DetailView, ListView
from order.models import OrderModel, OrderStatusType
from payment.models import PaymentStatusType

from dashboard.permissions import HasCustomerAccessPermission


class CustomerOrderListView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    template_name = "dashboard/customer/orders/order-list.html"
    paginate_by = 5

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = (
            OrderModel.objects.filter(user=self.request.user)
            .select_related("payment", "card_receipt")
            .prefetch_related("order_items", "order_items__product")
        )
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(id__icontains=search_q) | Q(tracking_code__icontains=search_q)
            )
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


class CustomerOrderDetailView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    template_name = "dashboard/customer/orders/order-detail.html"

    def get_queryset(self):
        return (
            OrderModel.objects.filter(user=self.request.user)
            .select_related("payment", "card_receipt")
            .prefetch_related("order_items", "order_items__product")
        )


class CustomerOrderInvoiceView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    template_name = "dashboard/customer/orders/order-invoice.html"

    def get_queryset(self):
        payment_confirmed = Q(
            payment__status__in=[
                PaymentStatusType.preparing.value,
                PaymentStatusType.shipped.value,
            ]
        )
        legacy_success_without_payment = Q(
            payment__isnull=True,
            status=OrderStatusType.success.value,
        )
        return (
            OrderModel.objects.filter(user=self.request.user)
            .select_related("payment", "user", "user__user_profile", "coupon")
            .prefetch_related("order_items", "order_items__product")
            .filter(payment_confirmed | legacy_success_without_payment)
        )

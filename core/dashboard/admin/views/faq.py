from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from dashboard.admin.forms import FAQItemForm
from dashboard.permissions import HasAdminAccessPermission
from website.models import FAQItem
from dashboard.mixins import DashboardDeviceTemplateMixin


class AdminFAQListView(DashboardDeviceTemplateMixin, LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/faq/faq-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = FAQItem.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(question__icontains=search_q) | Q(answer__icontains=search_q)
            )
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class AdminFAQCreateView(DashboardDeviceTemplateMixin, LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/faq/faq-create.html"
    queryset = FAQItem.objects.all()
    form_class = FAQItemForm
    success_url = reverse_lazy("dashboard:admin:faq-list")
    success_message = "سوال متداول با موفقیت ایجاد شد"


class AdminFAQEditView(DashboardDeviceTemplateMixin, LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/faq/faq-edit.html"
    queryset = FAQItem.objects.all()
    form_class = FAQItemForm
    success_message = "سوال متداول با موفقیت ویرایش شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:faq-edit", kwargs={"pk": self.get_object().pk})


class AdminFAQDeleteView(DashboardDeviceTemplateMixin, LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/faq/faq-delete.html"
    queryset = FAQItem.objects.all()
    success_url = reverse_lazy("dashboard:admin:faq-list")
    success_message = "سوال متداول با موفقیت حذف شد"

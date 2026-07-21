from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from dashboard.admin.forms import ProductTagForm
from dashboard.permissions import HasAdminAccessPermission
from shop.models import ProductTagModel


class AdminProductTagListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/tags/tag-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = ProductTagModel.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        else:
            queryset = queryset.order_by("title")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class AdminProductTagCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/tags/tag-create.html"
    queryset = ProductTagModel.objects.all()
    form_class = ProductTagForm
    success_url = reverse_lazy("dashboard:admin:product-tag-list")
    success_message = "ایجاد تگ محصول با موفقیت انجام شد"


class AdminProductTagEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/tags/tag-edit.html"
    queryset = ProductTagModel.objects.all()
    form_class = ProductTagForm
    success_message = "ویرایش تگ محصول با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-tag-edit", kwargs={"pk": self.get_object().pk})


class AdminProductTagDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/tags/tag-delete.html"
    queryset = ProductTagModel.objects.all()
    success_url = reverse_lazy("dashboard:admin:product-tag-list")
    success_message = "حذف تگ محصول با موفقیت انجام شد"

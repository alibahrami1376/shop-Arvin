from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import CategoryForm
from shop.models import ProductCategoryModel


class AdminCategoryListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/categories/category-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = ProductCategoryModel.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
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


class AdminCategoryCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/categories/category-create.html"
    queryset = ProductCategoryModel.objects.all()
    form_class = CategoryForm
    success_url = reverse_lazy("dashboard:admin:category-list")
    success_message = "ایجاد دسته‌بندی با موفقیت انجام شد"


class AdminCategoryEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/categories/category-edit.html"
    queryset = ProductCategoryModel.objects.all()
    form_class = CategoryForm
    success_message = "ویرایش دسته‌بندی با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:category-edit", kwargs={"pk": self.get_object().pk})


class AdminCategoryDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/categories/category-delete.html"
    queryset = ProductCategoryModel.objects.all()
    success_url = reverse_lazy("dashboard:admin:category-list")
    success_message = "حذف دسته‌بندی با موفقیت انجام شد"


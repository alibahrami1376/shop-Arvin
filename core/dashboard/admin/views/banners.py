from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from dashboard.admin.forms import DefaultHomeBannerForm, HomeBannerForm
from dashboard.permissions import HasAdminAccessPermission
from website.models import HomeBanner


class AdminHomeBannerListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/banners/banner-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = HomeBanner.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(title__icontains=search_q) | Q(link__icontains=search_q)
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


class AdminHomeBannerCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/banners/banner-create.html"
    queryset = HomeBanner.objects.all()
    form_class = HomeBannerForm
    success_url = reverse_lazy("dashboard:admin:home-banner-list")
    success_message = "بنر با موفقیت ایجاد شد"


class AdminHomeBannerEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/banners/banner-edit.html"
    queryset = HomeBanner.objects.all()
    def get_form_class(self):
        if self.get_object().is_default:
            return DefaultHomeBannerForm
        return HomeBannerForm

    def get_success_message(self, form):
        if self.get_object().is_default:
            return "وضعیت نمایش بنر پیش‌فرض ذخیره شد"
        return "بنر با موفقیت ویرایش شد"

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:home-banner-edit", kwargs={"pk": self.get_object().pk}
        )


class AdminHomeBannerDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/banners/banner-delete.html"
    queryset = HomeBanner.objects.all()
    success_url = reverse_lazy("dashboard:admin:home-banner-list")
    success_message = "بنر با موفقیت حذف شد"

    def dispatch(self, request, *args, **kwargs):
        banner = self.get_object()
        if banner.is_default:
            messages.error(request, "بنرهای پیش‌فرض قابل حذف نیستند؛ فقط می‌توانید غیرفعال کنید.")
            return redirect("dashboard:admin:home-banner-list")
        return super().dispatch(request, *args, **kwargs)

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from dashboard.admin.forms import CityForm, ProvinceForm
from dashboard.permissions import HasAdminAccessPermission
from order.models import City, Province


class AdminProvinceListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/locations/province-list.html"
    paginate_by = 20

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = Province.objects.annotate(cities_count=Count("cities"))
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(name__icontains=search_q)
        if active := self.request.GET.get("is_active"):
            if active in {"0", "1"}:
                queryset = queryset.filter(is_active=active == "1")
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        else:
            queryset = queryset.order_by("sort_order", "name")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class AdminProvinceCreateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView
):
    template_name = "dashboard/admin/locations/province-create.html"
    queryset = Province.objects.all()
    form_class = ProvinceForm
    success_message = "استان با موفقیت ایجاد شد"

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:province-edit", kwargs={"pk": self.object.pk}
        )


class AdminProvinceEditView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    template_name = "dashboard/admin/locations/province-edit.html"
    queryset = Province.objects.all()
    form_class = ProvinceForm
    success_message = "استان با موفقیت ویرایش شد"

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:province-edit", kwargs={"pk": self.object.pk}
        )


class AdminProvinceDeleteView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView
):
    template_name = "dashboard/admin/locations/province-delete.html"
    queryset = Province.objects.all()
    success_url = reverse_lazy("dashboard:admin:province-list")
    success_message = "استان با موفقیت حذف شد"

    def form_valid(self, form):
        province = self.get_object()
        cities_count = province.cities.count()
        response = super().form_valid(form)
        if cities_count:
            messages.info(
                self.request,
                f"{cities_count} شهر وابسته به این استان نیز حذف شد.",
            )
        return response


class AdminCityListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/locations/city-list.html"
    paginate_by = 20

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = City.objects.select_related("province")
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(name__icontains=search_q) | Q(province__name__icontains=search_q)
            )
        if province_id := self.request.GET.get("province"):
            queryset = queryset.filter(province_id=province_id)
        if active := self.request.GET.get("is_active"):
            if active in {"0", "1"}:
                queryset = queryset.filter(is_active=active == "1")
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        else:
            queryset = queryset.order_by(
                "province__sort_order", "province__name", "sort_order", "name"
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["provinces"] = Province.objects.order_by("sort_order", "name")
        context["selected_province"] = self.request.GET.get("province", "")
        return context


class AdminCityCreateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView
):
    template_name = "dashboard/admin/locations/city-create.html"
    queryset = City.objects.all()
    form_class = CityForm
    success_message = "شهر با موفقیت ایجاد شد"

    def get_initial(self):
        initial = super().get_initial()
        if province_id := self.request.GET.get("province"):
            initial["province"] = province_id
        return initial

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:city-edit", kwargs={"pk": self.object.pk})


class AdminCityEditView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    template_name = "dashboard/admin/locations/city-edit.html"
    queryset = City.objects.select_related("province")
    form_class = CityForm
    success_message = "شهر با موفقیت ویرایش شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:city-edit", kwargs={"pk": self.object.pk})


class AdminCityDeleteView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView
):
    template_name = "dashboard/admin/locations/city-delete.html"
    queryset = City.objects.select_related("province")
    success_message = "شهر با موفقیت حذف شد"

    def get_success_url(self):
        province_id = self.object.province_id
        return (
            reverse_lazy("dashboard:admin:city-list")
            + f"?province={province_id}"
        )

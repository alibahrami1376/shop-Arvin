import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from order.models import UserAddressModel

from dashboard.customer.forms import UserAddressForm
from dashboard.permissions import HasCustomerAccessPermission


def _address_list_context(request):
    queryset = UserAddressModel.objects.filter(user=request.user)
    if order_by := request.GET.get("order_by"):
        try:
            queryset = queryset.order_by(order_by)
        except FieldError:
            pass
    return {"object_list": queryset}


class CustomerAddressListView(
    LoginRequiredMixin, HasCustomerAccessPermission, ListView
):
    template_name = "dashboard/customer/addresses/address-list.html"
    htmx_template_name = (
        "dashboard/customer/addresses/partials/address-list-fragment.html"
    )

    def get_template_names(self):
        # Fragment فقط برای فیلتر/صفحه‌بندی؛ ناوبری داشبورد صفحه کامل می‌خواهد
        if (
            self.request.headers.get("HX-Request") == "true"
            and self.request.headers.get("HX-Target") == "customer-address-list-root"
        ):
            return [self.htmx_template_name]
        return [self.template_name]

    def get_queryset(self):
        queryset = UserAddressModel.objects.filter(user=self.request.user)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset


class CustomerAddressCreateView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, CreateView
):
    template_name = "dashboard/customer/addresses/address-create.html"
    form_class = UserAddressForm
    success_message = "ایجاد آدرس با موفقیت انجام شد"

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        return redirect(
            reverse_lazy(
                "dashboard:customer:address-edit", kwargs={"pk": form.instance.pk}
            )
        )

    def get_success_url(self):
        return reverse_lazy("dashboard:customer:address-list")


class CustomerAddressEditView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, UpdateView
):
    template_name = "dashboard/customer/addresses/address-edit.html"
    form_class = UserAddressForm
    success_message = "ویرایش آدرس با موفقیت انجام شد"

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:customer:address-edit", kwargs={"pk": self.get_object().pk}
        )


class CustomerAddressDeleteView(
    LoginRequiredMixin, HasCustomerAccessPermission, DeleteView
):
    template_name = "dashboard/customer/addresses/address-delete.html"
    success_url = reverse_lazy("dashboard:customer:address-list")
    success_message = "حذف آدرس با موفقیت انجام شد"

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, self.success_message)
        if request.headers.get("HX-Request") == "true":
            target = request.headers.get("HX-Target", "")
            if target == "customer-address-list-root":
                response = render(
                    request,
                    "dashboard/customer/addresses/partials/address-list-fragment.html",
                    _address_list_context(request),
                )
                response["HX-Trigger"] = json.dumps(
                    {
                        "showToast": {
                            "text": self.success_message,
                            "className": "success",
                            "background": "#2e7d32",
                            "duration": 2500,
                        }
                    }
                )
                return response
            response = HttpResponse(status=204)
            response["HX-Redirect"] = str(self.success_url)
            return response
        return redirect(self.success_url)

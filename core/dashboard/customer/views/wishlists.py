import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import FieldError
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView
from shop.models import WishlistProductModel

from dashboard.permissions import HasCustomerAccessPermission

DEFAULT_WISHLIST_PAGE_SIZE = 5


def _filtered_wishlist_queryset(request):
    queryset = WishlistProductModel.objects.filter(user=request.user)
    if search_q := request.GET.get("q"):
        queryset = queryset.filter(product__title__icontains=search_q)
    if order_by := request.GET.get("order_by"):
        try:
            queryset = queryset.order_by(order_by)
        except FieldError:
            pass
    return queryset


def _wishlist_list_context(request):
    queryset = _filtered_wishlist_queryset(request)
    try:
        page_size = int(request.GET.get("page_size", DEFAULT_WISHLIST_PAGE_SIZE))
    except (TypeError, ValueError):
        page_size = DEFAULT_WISHLIST_PAGE_SIZE
    if page_size < 1:
        page_size = DEFAULT_WISHLIST_PAGE_SIZE
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(request.GET.get("page"))
    return {
        "object_list": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "total_items": queryset.count(),
    }


class CustomerWishlistListView(
    LoginRequiredMixin, HasCustomerAccessPermission, ListView
):
    template_name = "dashboard/customer/wishlists/wishlist-list.html"
    htmx_template_name = (
        "dashboard/customer/wishlists/partials/wishlist-list-fragment.html"
    )
    paginate_by = DEFAULT_WISHLIST_PAGE_SIZE

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return [self.htmx_template_name]
        return [self.template_name]

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        return _filtered_wishlist_queryset(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class CustomerWishlistDeleteView(
    LoginRequiredMixin, HasCustomerAccessPermission, DeleteView
):
    http_method_names = ["post"]
    success_url = reverse_lazy("dashboard:customer:wishlist-list")
    success_message = "محصول با موفقیت از لیست حذف شد"

    def get_queryset(self):
        return WishlistProductModel.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get("HX-Request") == "true":
            response = render(
                request,
                "dashboard/customer/wishlists/partials/wishlist-list-fragment.html",
                _wishlist_list_context(request),
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
        messages.success(request, self.success_message)
        return redirect(self.success_url)

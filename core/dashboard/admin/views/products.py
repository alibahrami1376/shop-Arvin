from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models.base import Model as Model
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    View,
)
from shop.models import (
    ProductCategoryModel,
    ProductImageModel,
    ProductModel,
)

from dashboard.admin.forms import (
    ProductForm,
    ProductImageForm,
    ProductImageFormSet,
)
from dashboard.permissions import HasAdminAccessPermission


class AdminProductListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/products/product-list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = ProductModel.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if category_id := self.request.GET.get("category_id"):
            try:
                category = ProductCategoryModel.objects.get(pk=category_id)
                category_ids = category.get_self_and_descendant_ids()
                queryset = queryset.filter(category__id__in=category_ids)
            except (ProductCategoryModel.DoesNotExist, ValueError):
                pass
        if min_price := self.request.GET.get("min_price"):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.request.GET.get("max_price"):
            queryset = queryset.filter(price__lte=max_price)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        context["categories"] = ProductCategoryModel.get_tree_ordered()
        return context


class AdminProductCreateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView
):
    template_name = "dashboard/admin/products/product-create.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm
    success_message = "ایجاد محصول با موفقیت انجام شد"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ProductImageFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["image_formset"] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        form.instance.user = self.request.user
        self.object = form.save()

        if image_formset.is_valid():
            image_formset.instance = self.object
            image_formset.save()

        return redirect(
            reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": self.object.pk})
        )

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:product-list")


class AdminProductEditView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    template_name = "dashboard/admin/products/product-edit.html"
    queryset = ProductModel.objects.all()
    form_class = ProductForm
    success_message = "ویرایش محصول با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:product-edit", kwargs={"pk": self.get_object().pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = ProductImageForm()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.product_images.prefetch_related()
        return obj


class AdminProductDeleteView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView
):
    template_name = "dashboard/admin/products/product-delete.html"
    queryset = ProductModel.objects.all()
    success_url = reverse_lazy("dashboard:admin:product-list")
    success_message = "حذف محصول با موفقیت انجام شد"


class AdminProductAddImageView(
    LoginRequiredMixin, HasAdminAccessPermission, CreateView
):
    http_method_names = ["post"]
    form_class = ProductImageForm

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:product-edit", kwargs={"pk": self.kwargs.get("pk")}
        )

    def get_queryset(self):
        return ProductImageModel.objects.filter(product__id=self.kwargs.get("pk"))

    def form_valid(self, form):
        product = ProductModel.objects.get(pk=self.kwargs.get("pk"))
        form.instance.product = product
        if form.instance.sort_order is None or form.cleaned_data.get("sort_order") in (
            None,
            "",
        ):
            from django.db.models import Max

            max_order = product.product_images.aggregate(m=Max("sort_order")).get("m")
            form.instance.sort_order = (max_order or 0) + 1
        messages.success(self.request, "تصویر مورد نظر با موفقیت ثبت شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request, "اشکالی در ارسال تصویر رخ داد لطفا مجدد امتحان نمایید"
        )
        return redirect(
            reverse_lazy(
                "dashboard:admin:product-edit", kwargs={"pk": self.kwargs.get("pk")}
            )
        )


class AdminProductRemoveImageView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView
):
    http_method_names = ["post"]
    success_message = "تصویر مورد نظر با موفقیت حذف شد"

    def get_queryset(self):
        return ProductImageModel.objects.filter(product__id=self.kwargs.get("pk"))

    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs.get("image_id"))

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:product-edit", kwargs={"pk": self.kwargs.get("pk")}
        )

    def form_invalid(self, form):
        messages.error(
            self.request, "اشکالی در حذف تصویر رخ داد لطفا مجدد امتحان نمایید"
        )
        return redirect(
            reverse_lazy(
                "dashboard:admin:product-edit", kwargs={"pk": self.kwargs.get("pk")}
            )
        )


class AdminProductReorderImagesView(LoginRequiredMixin, HasAdminAccessPermission, View):
    """POST gallery image ids in desired order: image_ids=1,2,3"""

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        product = ProductModel.objects.get(pk=kwargs.get("pk"))
        raw = (request.POST.get("image_ids") or "").strip()
        ids = [int(x) for x in raw.split(",") if x.strip().isdigit()]
        images = {
            img.pk: img
            for img in ProductImageModel.objects.filter(product=product, pk__in=ids)
        }
        for index, image_id in enumerate(ids):
            img = images.get(image_id)
            if img:
                img.sort_order = index
                img.save(update_fields=["sort_order", "updated_date"])
        messages.success(request, "ترتیب گالری ذخیره شد")
        return redirect(
            reverse_lazy("dashboard:admin:product-edit", kwargs={"pk": product.pk})
        )

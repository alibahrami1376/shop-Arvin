from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import FieldError
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, View
from review.models import ReviewModel, ReviewStatusType

from core.seo import (
    breadcrumb_for_category,
    breadcrumb_for_product,
    breadcrumb_home_shop,
    breadcrumb_json_ld,
    normalize_meta_description,
)
from core.views_meta import ObjectMetadataMixin, SiteMetadataMixin

from .models import (
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
    WishlistProductModel,
)


class ShopProductListMixin:
    """Shared list/filter/pagination for product grid and category landings."""

    template_name = "shop/product-grid.html"
    paginate_by = 9

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_published_queryset(self):
        return ProductModel.objects.filter(status=ProductStatusType.publish.value)

    def apply_common_filters(self, queryset):
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
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

    def get_list_context_data(self, context):
        context["total_items"] = self.get_queryset().count()
        context["wishlist_items"] = (
            WishlistProductModel.objects.filter(user=self.request.user).values_list(
                "product__id", flat=True
            )
            if self.request.user.is_authenticated
            else []
        )
        context["categories"] = ProductCategoryModel.get_tree_ordered()
        return context


class ShopProductGridView(ShopProductListMixin, SiteMetadataMixin, ListView):
    title = f"محصولات - {settings.SITE_NAME}"
    description = (
        "لیست محصولات فروشگاه آروین؛ لوازم و قطعات کامیون را ببینید، "
        "مقایسه کنید و آنلاین سفارش دهید با ارسال سریع به سراسر کشور."
    )

    def dispatch(self, request, *args, **kwargs):
        category_id = request.GET.get("category_id")
        if category_id:
            try:
                category = ProductCategoryModel.objects.get(pk=category_id)
            except (ProductCategoryModel.DoesNotExist, ValueError, TypeError):
                pass
            else:
                params = request.GET.copy()
                params.pop("category_id", None)
                target = category.get_absolute_url()
                query = params.urlencode()
                if query:
                    target = f"{target}?{query}"
                return HttpResponsePermanentRedirect(target)
        return super().dispatch(request, *args, **kwargs)

    def get_meta_title(self, context=None):
        q = self.request.GET.get("q")
        if q:
            return f"جستجو: {q} - {settings.SITE_NAME}"
        return super().get_meta_title(context)

    def get_meta_description(self, context=None):
        q = self.request.GET.get("q")
        if q:
            return normalize_meta_description(
                f"نتایج جستجو برای «{q}» در فروشگاه آروین؛ "
                f"محصولات مرتبط با لوازم و قطعات کامیون را پیدا کنید."
            )
        return super().get_meta_description(context)

    def get_queryset(self):
        return self.apply_common_filters(self.get_published_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.get_list_context_data(context)
        items = [
            *breadcrumb_home_shop(),
            {"name": "محصولات", "url": self.request.path},
        ]
        context["breadcrumb_items"] = items
        context["breadcrumb_json_ld"] = breadcrumb_json_ld(items)
        return context


class ShopProductCategoryView(ShopProductListMixin, SiteMetadataMixin, ListView):
    """Category landing: /shop/category/<slug>/"""

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(ProductCategoryModel, slug=kwargs.get("slug"))
        return super().dispatch(request, *args, **kwargs)

    def get_meta_title(self, context=None):
        return f"{self.category.title} - {settings.SITE_NAME}"

    def get_meta_description(self, context=None):
        return normalize_meta_description(
            f"خرید {self.category.title} از فروشگاه آروین؛ محصولات این دسته را "
            f"مشاهده کنید و آنلاین سفارش دهید با ارسال سریع و پشتیبانی تخصصی."
        )

    def get_queryset(self):
        category_ids = self.category.get_self_and_descendant_ids()
        queryset = self.get_published_queryset().filter(category__id__in=category_ids)
        return self.apply_common_filters(queryset).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.get_list_context_data(context)
        context["active_category"] = self.category
        items = breadcrumb_for_category(self.category)
        context["breadcrumb_items"] = items
        context["breadcrumb_json_ld"] = breadcrumb_json_ld(items)
        return context


class ShopProductDetailView(ObjectMetadataMixin, DetailView):
    template_name = "shop/product-detail.html"
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        reviews = ReviewModel.objects.filter(
            product=product, status=ReviewStatusType.accepted.value
        ).select_related("user", "user__user_profile")
        context["reviews"] = reviews
        total_reviews_count = reviews.count()
        context["reviews_count"] = {
            f"rate_{rate}": reviews.filter(rate=rate).count() for rate in range(1, 6)
        }
        if total_reviews_count != 0:
            context["reviews_avg"] = {
                f"rate_{rate}": round(
                    (reviews.filter(rate=rate).count() / total_reviews_count) * 100, 2
                )
                for rate in range(1, 6)
            }
        else:
            context["reviews_avg"] = {f"rate_{rate}": 0 for rate in range(1, 6)}
        items = breadcrumb_for_product(product)
        context["breadcrumb_items"] = items
        context["breadcrumb_json_ld"] = breadcrumb_json_ld(items)
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.product_images.prefetch_related()
        return obj


class AddOrRemoveWishlistView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        message = ""
        if product_id:
            try:
                wishlist_item = WishlistProductModel.objects.get(
                    user=request.user, product__id=product_id
                )
                wishlist_item.delete()
                message = "محصول از لیست علایق حذف شد"
            except WishlistProductModel.DoesNotExist:
                WishlistProductModel.objects.create(
                    user=request.user, product_id=product_id
                )
                message = "محصول به لیست علایق اضافه شد"

        return JsonResponse({"message": message})

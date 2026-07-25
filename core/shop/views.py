from django.conf import settings
from django.views.generic import (
    ListView,
    DetailView,
    View
)
from .models import ProductModel, ProductStatusType, ProductCategoryModel, WishlistProductModel
from django.core.exceptions import FieldError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from review.models import ReviewModel, ReviewStatusType
from core.views_meta import ObjectMetadataMixin, SiteMetadataMixin


class ShopProductGridView(SiteMetadataMixin, ListView):
    template_name = "shop/product-grid.html"
    paginate_by = 9
    title = f"محصولات - {settings.SITE_NAME}"
    description = "مشاهده و خرید محصولات فروشگاه آروین."

    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)

    def get_meta_title(self, context=None):
        category_id = self.request.GET.get("category_id")
        if category_id:
            try:
                category = ProductCategoryModel.objects.get(pk=category_id)
                return f"{category.title} - {settings.SITE_NAME}"
            except (ProductCategoryModel.DoesNotExist, ValueError):
                pass
        q = self.request.GET.get("q")
        if q:
            return f"جستجو: {q} - {settings.SITE_NAME}"
        return super().get_meta_title(context)

    def get_queryset(self):
        queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value)
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
        context["wishlist_items"] = WishlistProductModel.objects.filter(user=self.request.user).values_list(
            "product__id", flat=True) if self.request.user.is_authenticated else []
        context["categories"] = ProductCategoryModel.get_tree_ordered()
        return context


class ShopProductDetailView(ObjectMetadataMixin, DetailView):
    template_name = "shop/product-detail.html"
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value)

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
                    user=request.user, product__id=product_id)
                wishlist_item.delete()
                message = "محصول از لیست علایق حذف شد"
            except WishlistProductModel.DoesNotExist:
                WishlistProductModel.objects.create(
                    user=request.user, product_id=product_id)
                message = "محصول به لیست علایق اضافه شد"

        return JsonResponse({"message": message})

from django.urls import path, re_path

from . import views

app_name = "shop"

urlpatterns = [
    path("product/grid/", views.ShopProductGridView.as_view(), name="product-grid"),
    re_path(
        r"category/(?P<slug>[-\w]+)/$",
        views.ShopProductCategoryView.as_view(),
        name="product-category",
    ),
    re_path(
        r"product/(?P<slug>[-\w]+)/$",
        views.ShopProductDetailView.as_view(),
        name="product-detail",
    ),
    re_path(
        r"product/(?P<slug>[-\w]+)/detail/",
        views.product_detail_legacy_redirect,
        name="product-detail-legacy",
    ),
    path(
        "add-or-remove-wishlist/",
        views.AddOrRemoveWishlistView.as_view(),
        name="add-or-remove-wishlist",
    ),
]

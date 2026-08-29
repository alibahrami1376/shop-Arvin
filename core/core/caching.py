"""LocMem helpers for public, low-churn site data (not cart/checkout/payments)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.core.cache import cache

# Keys
KEY_SITE_BRANDING = "site_branding"
KEY_SITE_SOCIAL_LINKS = "site_social_links"
KEY_CONTACT_SETTINGS = "contact_settings"
KEY_SHOP_CATEGORIES = "shop_categories"
KEY_FAQ_PUBLISHED = "faq_published"
KEY_HOME_TOP_PRODUCTS = "home_top_products"
KEY_HOME_NEWEST = "home_newest"
KEY_HOME_BESTSELLERS = "home_bestsellers"
KEY_HOME_LATEST_POSTS = "home_latest_posts"

TTL_SETTINGS = 300  # ~5 min — branding, nav, FAQ, legal
TTL_HOME = 90  # ~1.5 min — home product/post fragments


def home_banners_key(device: str) -> str:
    return f"home_banners:{device}"


def legal_page_key(page_type: str) -> str:
    return f"legal:{page_type}"


def get_or_set(
    key: str,
    producer: Callable[[], Any],
    timeout: int = TTL_SETTINGS,
) -> Any:
    """Return cached value or call producer (evaluated data, not a QuerySet)."""
    value = cache.get(key)
    if value is not None:
        return value
    value = producer()
    cache.set(key, value, timeout)
    return value


def invalidate(*keys: str) -> None:
    if keys:
        cache.delete_many(keys)


def invalidate_home_product_fragments() -> None:
    invalidate(
        KEY_HOME_TOP_PRODUCTS,
        KEY_HOME_NEWEST,
        KEY_HOME_BESTSELLERS,
    )


def get_site_branding():
    from website.models import SiteBrandingSettings

    return get_or_set(
        KEY_SITE_BRANDING,
        SiteBrandingSettings.get_solo,
        timeout=TTL_SETTINGS,
    )


def get_site_social_links():
    from website.models import SiteWideSocialSettings

    def _load():
        return SiteWideSocialSettings.get_solo().get_links()

    return get_or_set(KEY_SITE_SOCIAL_LINKS, _load, timeout=TTL_SETTINGS)


def get_contact_settings():
    from website.models import ContactPageSettings

    return get_or_set(
        KEY_CONTACT_SETTINGS,
        ContactPageSettings.get_solo,
        timeout=TTL_SETTINGS,
    )


def get_shop_categories():
    from django.db.models import Prefetch
    from shop.models import ProductCategoryModel

    def _load():
        children_qs = ProductCategoryModel.objects.order_by("title")
        qs = (
            ProductCategoryModel.objects.filter(parent__isnull=True)
            .prefetch_related(Prefetch("children", queryset=children_qs))
            .order_by("id")
        )
        return list(qs)

    return get_or_set(KEY_SHOP_CATEGORIES, _load, timeout=TTL_SETTINGS)


def get_home_banners(device: str):
    from website.models import HomeBanner

    key = home_banners_key(device)
    allowed = ("all", "mobile") if device == "mobile" else ("all", "desktop")

    def _load():
        return list(
            HomeBanner.objects.filter(
                is_active=True,
                display_target__in=allowed,
            )
        )

    return get_or_set(key, _load, timeout=TTL_SETTINGS)


def get_faq_published():
    from website.models import FAQItem

    def _load():
        return list(FAQItem.objects.filter(is_published=True))

    return get_or_set(KEY_FAQ_PUBLISHED, _load, timeout=TTL_SETTINGS)


def get_legal_page(page_type: str):
    from website.models import LegalPage

    return get_or_set(
        legal_page_key(page_type),
        lambda: LegalPage.get_by_type(page_type),
        timeout=TTL_SETTINGS,
    )


def get_home_top_products():
    from shop.models import ProductModel, ProductStatusType

    def _load():
        return list(
            ProductModel.objects.filter(status=ProductStatusType.publish.value)
            .prefetch_related("category")
            .order_by("-avg_rate", "-created_date")[:8]
        )

    return get_or_set(KEY_HOME_TOP_PRODUCTS, _load, timeout=TTL_HOME)


def get_home_newest_products():
    from shop.models import ProductModel, ProductStatusType

    def _load():
        return list(
            ProductModel.objects.filter(status=ProductStatusType.publish.value)
            .prefetch_related("category")
            .order_by("-created_date")[:4]
        )

    return get_or_set(KEY_HOME_NEWEST, _load, timeout=TTL_HOME)


def get_home_bestseller_products():
    from django.db.models import IntegerField, Q, Sum, Value
    from django.db.models.functions import Coalesce
    from order.models import OrderStatusType
    from shop.models import ProductModel, ProductStatusType

    def _load():
        order_success = OrderStatusType.success.value
        return list(
            ProductModel.objects.filter(status=ProductStatusType.publish.value)
            .prefetch_related("category")
            .annotate(
                sold_qty=Coalesce(
                    Sum(
                        "orderitemmodel__quantity",
                        filter=Q(orderitemmodel__order__status=order_success),
                    ),
                    Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("-sold_qty", "-avg_rate")[:4]
        )

    return get_or_set(KEY_HOME_BESTSELLERS, _load, timeout=TTL_HOME)


def get_home_latest_posts():
    from blog.models import Post

    def _load():
        return list(
            Post.objects.filter(status=True)
            .select_related("author")
            .prefetch_related("category")
            .order_by("-published_date", "-created_date")[:3]
        )

    return get_or_set(KEY_HOME_LATEST_POSTS, _load, timeout=TTL_HOME)

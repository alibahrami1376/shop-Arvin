"""Best-effort LocMem invalidation on admin/model writes (per-process only)."""

from django.db.models.signals import post_delete, post_save

from core.caching import (
    KEY_CONTACT_SETTINGS,
    KEY_FAQ_PUBLISHED,
    KEY_HOME_LATEST_POSTS,
    KEY_SHOP_CATEGORIES,
    KEY_SITE_BRANDING,
    KEY_SITE_SOCIAL_LINKS,
    home_banners_key,
    invalidate,
    invalidate_home_product_fragments,
    legal_page_key,
)


def _connect_cache_signals():
    from blog.models import Post
    from shop.models import ProductCategoryModel, ProductModel
    from website.models import (
        ContactPageSettings,
        FAQItem,
        HomeBanner,
        LegalPage,
        SiteBrandingSettings,
        SiteWideSocialSettings,
    )

    def clear_branding(**kwargs):
        invalidate(KEY_SITE_BRANDING)

    def clear_social(**kwargs):
        invalidate(KEY_SITE_SOCIAL_LINKS)

    def clear_contact(**kwargs):
        invalidate(KEY_CONTACT_SETTINGS)

    def clear_categories(**kwargs):
        invalidate(KEY_SHOP_CATEGORIES)

    def clear_banners(**kwargs):
        invalidate(home_banners_key("mobile"), home_banners_key("desktop"))

    def clear_faq(**kwargs):
        invalidate(KEY_FAQ_PUBLISHED)

    def clear_legal(instance, **kwargs):
        invalidate(legal_page_key(instance.page_type))

    def clear_home_products(**kwargs):
        invalidate_home_product_fragments()

    def clear_home_posts(**kwargs):
        invalidate(KEY_HOME_LATEST_POSTS)

    pairs = (
        (SiteBrandingSettings, clear_branding),
        (SiteWideSocialSettings, clear_social),
        (ContactPageSettings, clear_contact),
        (ProductCategoryModel, clear_categories),
        (HomeBanner, clear_banners),
        (FAQItem, clear_faq),
        (LegalPage, clear_legal),
        (ProductModel, clear_home_products),
        (Post, clear_home_posts),
    )
    for model, handler in pairs:
        post_save.connect(handler, sender=model, weak=False)
        post_delete.connect(handler, sender=model, weak=False)

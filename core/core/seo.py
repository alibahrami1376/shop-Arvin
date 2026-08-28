"""Helpers for technical SEO (canonical URLs, robots meta, etc.)."""

import re

from django.conf import settings
from django.utils.html import strip_tags

# Reserved for later: if we keep selected query params on canonical, strip these.
STRIP_QUERY_KEYS = frozenset(
    {
        "site",
        "sort",
        "order_by",
    }
)

# Align with robots.txt Disallow — private / transactional URLs.
NOINDEX_PATH_PREFIXES = (
    "/admin/",
    "/dashboard/",
    "/accounts/",
    "/cart/",
    "/order/",
    "/payment/",
    "/api/",
    "/ckeditor5/",
)

# Target length for meta description (Google snippet guidance).
META_DESCRIPTION_MAX_LENGTH = 160


def normalize_meta_description(
    text: str | None,
    *,
    max_length: int = META_DESCRIPTION_MAX_LENGTH,
) -> str:
    """Strip HTML, collapse whitespace, and truncate for meta description."""
    if not text:
        return ""
    cleaned = strip_tags(str(text))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) <= max_length:
        return cleaned
    truncated = cleaned[: max_length + 1]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    else:
        truncated = cleaned[:max_length]
    return truncated.rstrip(" ،,.;:") + "…"


def build_canonical_url(request) -> str:
    """
    Self-referential canonical: https://domain + path, without query string.

    Drops ?site=, filters, and sort so layout/filter variants share one URL.
    Meaningful params (e.g. page) can be allow-listed later using STRIP_QUERY_KEYS.
    """
    path = request.path or "/"
    return absolute_site_url(path)


def absolute_site_url(path_or_url: str) -> str:
    """Build https://SITE_DOMAIN/... from a path; leave absolute http(s) URLs as-is."""
    if not path_or_url:
        return ""
    value = str(path_or_url).strip()
    if value.startswith(("http://", "https://")):
        return value
    protocol = getattr(settings, "META_SITE_PROTOCOL", "https")
    domain = settings.SITE_DOMAIN
    if not value.startswith("/"):
        value = f"/{value}"
    return f"{protocol}://{domain}{value}"


def should_noindex(path: str) -> bool:
    path = path or "/"
    if not path.endswith("/"):
        path = f"{path}/"
    return any(path.startswith(prefix) for prefix in NOINDEX_PATH_PREFIXES)


def get_meta_robots(request) -> str:
    """Default indexable; noindex for private/transactional paths."""
    if should_noindex(request.path):
        return "noindex,follow"
    return "index,follow"


def breadcrumb_json_ld(items: list[dict]) -> str:
    """
    Build BreadcrumbList JSON-LD from UI items.

    Each item: {"name": str, "url": str} — url may be a path or absolute URL.
    """
    import json

    elements = []
    for position, item in enumerate(items, start=1):
        name = (item.get("name") or "").strip()
        if not name:
            continue
        entry = {
            "@type": "ListItem",
            "position": position,
            "name": name,
        }
        url = item.get("url")
        if url:
            entry["item"] = absolute_site_url(url)
        elements.append(entry)
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def breadcrumb_home_shop() -> list[dict]:
    from django.urls import reverse

    return [
        {"name": "خانه", "url": reverse("website:index")},
        {"name": "فروشگاه", "url": reverse("shop:product-grid")},
    ]


def breadcrumb_for_category(category) -> list[dict]:
    items = breadcrumb_home_shop()
    chain = []
    node = category
    while node is not None:
        chain.append(node)
        node = getattr(node, "parent", None)
    for cat in reversed(chain):
        items.append({"name": cat.title, "url": cat.get_absolute_url()})
    return items


def breadcrumb_for_product(product) -> list[dict]:
    items = breadcrumb_home_shop()
    category = product.category.select_related("parent").order_by("title").first()
    if category is not None:
        chain = []
        node = category
        while node is not None:
            chain.append(node)
            node = getattr(node, "parent", None)
        for cat in reversed(chain):
            items.append({"name": cat.title, "url": cat.get_absolute_url()})
    items.append({"name": product.title, "url": product.get_absolute_url()})
    return items


def breadcrumb_for_blog_post(post) -> list[dict]:
    from django.urls import reverse

    items = [
        {"name": "خانه", "url": reverse("website:index")},
        {"name": "بلاگ", "url": reverse("blog:blog_home")},
    ]
    category = post.category.order_by("name").first()
    if category is not None:
        items.append(
            {
                "name": category.name,
                "url": reverse("blog:category", kwargs={"cat_name": category.name}),
            }
        )
    items.append({"name": post.title, "url": post.get_absolute_url()})
    return items


def breadcrumb_for_blog_list(*, cat_name: str | None = None) -> list[dict]:
    from django.urls import reverse

    items = [
        {"name": "خانه", "url": reverse("website:index")},
        {"name": "بلاگ", "url": reverse("blog:blog_home")},
    ]
    if cat_name:
        items.append(
            {
                "name": cat_name,
                "url": reverse("blog:category", kwargs={"cat_name": cat_name}),
            }
        )
    return items


def faq_page_json_ld(faq_items) -> str:
    """Build FAQPage JSON-LD from published FAQItem queryset or list."""
    import json

    entities = []
    for item in faq_items:
        question = (item.question or "").strip()
        answer = strip_tags(str(item.answer or ""))
        answer = re.sub(r"\s+", " ", answer).strip()
        if not question or not answer:
            continue
        entities.append(
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer,
                },
            }
        )
    if not entities:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

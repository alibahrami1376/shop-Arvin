"""Helpers for technical SEO (canonical URLs, robots meta, etc.)."""

from django.conf import settings

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


def build_canonical_url(request) -> str:
    """
    Self-referential canonical: https://domain + path, without query string.

    Drops ?site=, filters, and sort so layout/filter variants share one URL.
    Meaningful params (e.g. page) can be allow-listed later using STRIP_QUERY_KEYS.
    """
    protocol = getattr(settings, "META_SITE_PROTOCOL", "https")
    domain = settings.SITE_DOMAIN
    path = request.path or "/"
    return f"{protocol}://{domain}{path}"


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

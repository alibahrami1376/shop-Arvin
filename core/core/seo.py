"""Helpers for technical SEO (canonical URLs, etc.)."""

from django.conf import settings

# Reserved for later: if we keep selected query params on canonical, strip these.
STRIP_QUERY_KEYS = frozenset(
    {
        "site",
        "sort",
        "order_by",
    }
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

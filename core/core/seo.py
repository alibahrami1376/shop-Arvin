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

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


FALLBACK_STATIC = "img/900x900/img1.jpg"


def _static_fallback_url():
    try:
        return staticfiles_storage.url(FALLBACK_STATIC)
    except Exception:
        return f"{settings.STATIC_URL}{FALLBACK_STATIC}"


def safe_imagekit_url(instance, spec_attr, source_attr="image"):
    """
    Return processed ImageKit URL, or fall back to the original / static file.
    Never returns a CACHE URL when the source file is missing on disk.
    """
    source = getattr(instance, source_attr, None)
    if not source:
        return _static_fallback_url()

    name = getattr(source, "name", "") or ""
    if not name or name.startswith("/"):
        return _static_fallback_url()

    try:
        if not source.storage.exists(name):
            return _static_fallback_url()
    except Exception:
        return _static_fallback_url()

    try:
        spec = getattr(instance, spec_attr)
        url = spec.url
        cache_name = getattr(spec, "name", "") or ""
        if cache_name and not spec.storage.exists(cache_name):
            return source.url
        return url
    except Exception:
        try:
            return source.url
        except Exception:
            return _static_fallback_url()

def safe_imagekit_url(instance, spec_attr, source_attr="image"):
    """
    Return processed ImageKit URL, or fall back to the original file URL.
    Skips processing for empty / absolute-default paths that break storage.
    """
    source = getattr(instance, source_attr, None)
    if not source:
        return ""
    name = getattr(source, "name", "") or ""
    if not name or name.startswith("/"):
        try:
            return source.url
        except Exception:
            return ""
    try:
        return getattr(instance, spec_attr).url
    except Exception:
        try:
            return source.url
        except Exception:
            return ""

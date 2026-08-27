"""Project-wide django-meta helpers for CBVs."""

from django.conf import settings
from meta.views import MetadataMixin

from core.seo import normalize_meta_description


class SiteMetadataMixin(MetadataMixin):
    """Base meta for public pages — defaults + site name from settings."""

    site_name = settings.SITE_NAME
    locale = "fa_IR"
    description = settings.META_DEFAULT_DESCRIPTION

    def get_meta_site_name(self, context=None):
        return self.site_name or settings.SITE_NAME

    def get_meta_url(self, context=None):
        if self.url:
            return self.url
        return self.request.path

    def get_meta_description(self, context=None):
        raw = super().get_meta_description(context)
        normalized = normalize_meta_description(raw)
        if normalized:
            return normalized
        return normalize_meta_description(settings.META_DEFAULT_DESCRIPTION)


class ObjectMetadataMixin(SiteMetadataMixin):
    """
    For DetailView (or similar): after building context, prefer
    ``object.as_meta(request)`` when the model uses ModelMeta.
    """

    meta_object_context_key = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context.get(self.meta_object_context_key)
        if obj is not None and hasattr(obj, "as_meta"):
            context[self.context_meta_name] = obj.as_meta(self.request)
        return context

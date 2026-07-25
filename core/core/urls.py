from django.contrib import admin
from django.contrib.sitemaps.views import index as sitemap_index
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from website.pwa_views import ServiceWorkerView, WebAppManifestView

from core.error_views import page_not_found, permission_denied, server_error
from core.sitemaps import (
    BlogCategorySitemap,
    BlogPostSitemap,
    ProductCategorySitemap,
    ProductSitemap,
    StaticViewSitemap,
)

handler404 = page_not_found
handler403 = permission_denied
handler500 = server_error

sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
    "product-categories": ProductCategorySitemap,
    "blog": BlogPostSitemap,
    "blog-categories": BlogCategorySitemap,
}


class RobotsTxtView(TemplateView):
    template_name = "robots.txt"
    content_type = "text/plain"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = getattr(self.request, "site", None)
        domain = site.domain if site is not None else settings.SITE_DOMAIN
        protocol = "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else self.request.scheme
        context["sitemap_url"] = f"{protocol}://{domain}{reverse('sitemap-index')}"
        return context


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'sitemap.xml',
        sitemap_index,
        {'sitemaps': sitemaps},
        name='sitemap-index',
    ),
    path(
        'sitemap-<section>.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('robots.txt', RobotsTxtView.as_view(), name='robots-txt'),
    path('manifest.webmanifest', WebAppManifestView.as_view(), name='pwa-manifest'),
    path('sw.js', ServiceWorkerView.as_view(), name='pwa-service-worker'),
    path('', include('website.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/accounts/', include('accounts.api_urls')),
    path('shop/', include('shop.urls')),
    path('cart/', include('cart.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('order/', include('order.urls')),
    path('payment/', include('payment.urls')),
    path('review/', include('review.urls')),
    path('blog/', include('blog.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    # از finders (شامل پکیج django_ckeditor_5) سرو می‌شود؛ نه فقط STATIC_ROOT.
    # در غیر این صورت بدون collectstatic روی /app/static، bundle.js ادیتور 404 می‌شود.
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from website.pwa_views import ServiceWorkerView, WebAppManifestView

from core.error_views import page_not_found, permission_denied, server_error

handler404 = page_not_found
handler403 = permission_denied
handler500 = server_error

urlpatterns = [
    path('admin/', admin.site.urls),
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
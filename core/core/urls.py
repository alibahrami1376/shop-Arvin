from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('accounts/', include('accounts.urls')),
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
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
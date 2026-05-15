from django.urls import path

from .. import views

urlpatterns = [
    path("banners/list/", views.AdminHomeBannerListView.as_view(), name="home-banner-list"),
    path("banners/create/", views.AdminHomeBannerCreateView.as_view(), name="home-banner-create"),
    path("banners/<int:pk>/edit/", views.AdminHomeBannerEditView.as_view(), name="home-banner-edit"),
    path(
        "banners/<int:pk>/delete/",
        views.AdminHomeBannerDeleteView.as_view(),
        name="home-banner-delete",
    ),
]

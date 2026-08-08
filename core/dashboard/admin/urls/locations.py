from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path(
        "locations/province/list/",
        views.AdminProvinceListView.as_view(),
        name="province-list",
    ),
    path(
        "locations/province/create/",
        views.AdminProvinceCreateView.as_view(),
        name="province-create",
    ),
    path(
        "locations/province/<int:pk>/edit/",
        views.AdminProvinceEditView.as_view(),
        name="province-edit",
    ),
    path(
        "locations/province/<int:pk>/delete/",
        views.AdminProvinceDeleteView.as_view(),
        name="province-delete",
    ),
    path(
        "locations/city/list/",
        views.AdminCityListView.as_view(),
        name="city-list",
    ),
    path(
        "locations/city/create/",
        views.AdminCityCreateView.as_view(),
        name="city-create",
    ),
    path(
        "locations/city/<int:pk>/edit/",
        views.AdminCityEditView.as_view(),
        name="city-edit",
    ),
    path(
        "locations/city/<int:pk>/delete/",
        views.AdminCityDeleteView.as_view(),
        name="city-delete",
    ),
]

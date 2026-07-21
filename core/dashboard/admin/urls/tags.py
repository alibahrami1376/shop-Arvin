from django.urls import path

from .. import views

urlpatterns = [
    path("tag/list/", views.AdminProductTagListView.as_view(), name="product-tag-list"),
    path("tag/create/", views.AdminProductTagCreateView.as_view(), name="product-tag-create"),
    path("tag/<int:pk>/edit/", views.AdminProductTagEditView.as_view(), name="product-tag-edit"),
    path("tag/<int:pk>/delete/", views.AdminProductTagDeleteView.as_view(), name="product-tag-delete"),
]

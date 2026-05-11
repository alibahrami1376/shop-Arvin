from django.urls import path
from .. import views


urlpatterns = [
    path("category/list/", views.AdminCategoryListView.as_view(), name="category-list"),
    path("category/create/", views.AdminCategoryCreateView.as_view(), name="category-create"),
    path("category/<int:pk>/edit/", views.AdminCategoryEditView.as_view(), name="category-edit"),
    path("category/<int:pk>/delete/", views.AdminCategoryDeleteView.as_view(), name="category-delete"),
]


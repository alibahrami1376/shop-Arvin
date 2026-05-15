from django.urls import path

from .. import views

urlpatterns = [
    path("faq/list/", views.AdminFAQListView.as_view(), name="faq-list"),
    path("faq/create/", views.AdminFAQCreateView.as_view(), name="faq-create"),
    path("faq/<int:pk>/edit/", views.AdminFAQEditView.as_view(), name="faq-edit"),
    path("faq/<int:pk>/delete/", views.AdminFAQDeleteView.as_view(), name="faq-delete"),
]

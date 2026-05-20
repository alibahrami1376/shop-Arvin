from django.urls import path

from .. import views

urlpatterns = [
    path(
        "settings/branding/",
        views.AdminSiteBrandingSettingsView.as_view(),
        name="site-branding-settings",
    ),
    path(
        "settings/site-social/",
        views.AdminSiteWideSocialSettingsView.as_view(),
        name="site-wide-social-settings",
    ),
    path(
        "settings/contact/",
        views.AdminContactPageSettingsView.as_view(),
        name="contact-settings",
    ),
    path(
        "settings/legal/<str:page_type>/",
        views.AdminLegalPageUpdateView.as_view(),
        name="legal-page-edit",
    ),
]

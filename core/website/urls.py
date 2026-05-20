from django.urls import path
from . import views
app_name = "website"

urlpatterns = [
    path("",views.IndexView.as_view(),name="index"),
    path("contact/",views.ContactView.as_view(),name="contact"),
    path("about/",views.AboutView.as_view(),name="about"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("privacy/", views.LegalPageView.as_view(), {"page_type": "privacy"}, name="privacy"),
    path("terms/", views.LegalPageView.as_view(), {"page_type": "terms"}, name="terms"),
    path("submit/ticket/", views.SendContactView.as_view(), name="submit-ticket"),
    path("newsletter/", views.NewsletterView.as_view(), name="newsletter"),
]
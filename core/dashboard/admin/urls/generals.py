from django.urls import path, include
from .. import views


urlpatterns = [

    path("home/", views.AdminDashboardHomeView.as_view(), name="home"),
    path(
        "settings/card-to-card/",
        views.AdminCardToCardSettingsView.as_view(),
        name="card-to-card-settings",
    ),
    path(
        "settings/payment-methods/",
        views.AdminPaymentMethodSettingsView.as_view(),
        name="payment-method-settings",
    ),
]

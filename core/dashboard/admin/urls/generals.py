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
    path(
        "settings/sms/",
        views.AdminSMSSettingsView.as_view(),
        name="sms-settings",
    ),
    path(
        "settings/checkout-pricing/",
        views.AdminCheckoutPricingSettingsView.as_view(),
        name="checkout-pricing-settings",
    ),
]

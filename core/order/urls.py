from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    path("track/", views.OrderTrackingView.as_view(), name="track"),
    path(
        "validate-coupon/", views.ValidateCouponView.as_view(), name="validate-coupon"
    ),
    path("checkout/", views.OrderCheckOutView.as_view(), name="checkout"),
    path(
        "card-payment/<int:pk>/",
        views.CardPaymentInstructionsView.as_view(),
        name="card-payment-instructions",
    ),
    path(
        "card-payment/<int:pk>/receipt-sent/",
        views.CardReceiptConfirmationView.as_view(),
        name="card-receipt-confirmation",
    ),
    path(
        "bale-payment/<int:pk>/",
        views.BalePaymentInstructionsView.as_view(),
        name="bale-payment-instructions",
    ),
    path(
        "bale-payment/<int:pk>/status/",
        views.BalePaymentStatusView.as_view(),
        name="bale-payment-status",
    ),
    path(
        "bale-payment/<int:pk>/inquire/",
        views.BalePaymentInquireView.as_view(),
        name="bale-payment-inquire",
    ),
    path("completed/", views.OrderCompletedView.as_view(), name="completed"),
    path("failed/", views.OrderFailedView.as_view(), name="failed"),
]

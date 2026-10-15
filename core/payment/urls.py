from django.urls import path

from . import views

app_name = "payment"

urlpatterns = [
    path("verify", views.PaymentVerifyView.as_view(), name="verify"),
    path(
        "bale/bot-webhook/",
        views.BaleBotWebhookView.as_view(),
        name="bale-bot-webhook",
    ),
]

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "register/send-otp/",
        views.WebRegisterSendOTPView.as_view(),
        name="register-send-otp",
    ),
    path(
        "password-reset/",
        views.PasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset/send-otp/",
        views.PasswordResetSendOTPView.as_view(),
        name="password-reset-send-otp",
    ),
]

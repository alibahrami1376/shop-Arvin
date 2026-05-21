"""
مسیرهای API حساب کاربری (prefix: /api/accounts/).
"""

from django.urls import path

from accounts import views

urlpatterns = [
    path("register/email/", views.RegisterEmailView.as_view(), name="api-register-email"),
    path(
        "register/phone/",
        views.RegisterPhoneView.as_view(),
        name="api-register-phone",
    ),
    path(
        "register/phone/send-otp/",
        views.SendOTPView.as_view(),
        name="api-register-send-otp",
    ),
    path(
        "register/phone/verify-otp/",
        views.VerifyOTPRegisterView.as_view(),
        name="api-register-verify-otp",
    ),
    path("login/", views.LoginAPIView.as_view(), name="api-login"),
    path(
        "verify-phone/send-otp/",
        views.SendVerifyPhoneOTPView.as_view(),
        name="api-verify-phone-send-otp",
    ),
    path(
        "verify-phone/verify-otp/",
        views.VerifyPhoneOTPView.as_view(),
        name="api-verify-phone-verify-otp",
    ),
]

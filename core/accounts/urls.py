from django.urls import path
from . import views

app_name = "accounts"

# مسیرهای REST زیر /api/accounts/ در فایل accounts/api_urls.py تعریف شده‌اند
# و در core/urls.py با path('api/accounts/', include('accounts.api_urls')) وصل می‌شوند.

urlpatterns = [
    #path('',include('django.contrib.auth.urls'))
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path(
        "register/send-otp/",
        views.WebRegisterSendOTPView.as_view(),
        name="register-send-otp",
    ),
    path(
        "verify-phone/web/send-otp/",
        views.WebSendVerifyPhoneOTPView.as_view(),
        name="web-verify-phone-send-otp",
    ),
    path(
        "verify-phone/web/verify-otp/",
        views.WebVerifyPhoneOTPView.as_view(),
        name="web-verify-phone-verify-otp",
    ),
]
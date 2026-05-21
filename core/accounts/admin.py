from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import Profile, SMSSettings

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """پنل مدیریت کاربران؛ شناسه ورود = شماره موبایل."""

    model = User
    list_display = (
        "id",
        "phone_number",
        "phone_verified",
        "email",
        "is_superuser",
        "is_active",
        "is_verified",
    )
    list_filter = ("is_superuser", "is_active", "is_verified", "phone_verified", "type")
    search_fields = ("phone_number", "email")
    ordering = ("id",)
    fieldsets = (
        (
            "احراز هویت",
            {
                "fields": ("email", "phone_number", "password"),
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "phone_verified",
                    "type",
                ),
            },
        ),
        (
            "گروه‌ها و دسترسی‌ها",
            {
                "fields": ("groups", "user_permissions"),
            },
        ),
        (
            "تاریخ‌ها",
            {
                "fields": ("last_login",),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "phone_verified",
                    "type",
                ),
            },
        ),
    )


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name")
    search_fields = ("user__email", "user__phone_number", "first_name", "last_name")


@admin.register(SMSSettings)
class SMSSettingsAdmin(admin.ModelAdmin):
    """فقط یک ردیف؛ از پنل ادمین ارسال پیامک OTP را روشن/خاموش کنید."""

    list_display = ("id", "sms_enabled", "updated_date")
    fields = ("sms_enabled",)

    def has_add_permission(self, request):
        return not SMSSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(User, CustomUserAdmin)

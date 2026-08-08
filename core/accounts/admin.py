from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import OTPCode, Profile

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """پنل مدیریت کاربران."""

    model = User
    list_display = (
        "id",
        "phone_number",
        "email",
        "is_superuser",
        "is_active",
        "is_verified",
    )
    list_filter = ("is_superuser", "is_active", "is_verified", "type")
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
                    "type",
                ),
            },
        ),
    )


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name")
    search_fields = ("user__email", "user__phone_number", "first_name", "last_name")


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """مدیریت کدهای OTP ثبت‌نام / تأیید موبایل."""

    list_display = (
        "id",
        "mobile",
        "code",
        "user",
        "is_used",
        "is_currently_valid",
        "created_at",
    )
    list_filter = ("is_used", "created_at")
    search_fields = ("mobile", "code", "user__email", "user__phone_number")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "is_currently_valid")
    raw_id_fields = ("user",)
    list_select_related = ("user",)
    date_hierarchy = "created_at"

    fieldsets = (
        (
            None,
            {
                "fields": ("user", "mobile", "code", "is_used"),
            },
        ),
        (
            "وضعیت",
            {
                "fields": ("created_at", "is_currently_valid"),
            },
        ),
    )

    @admin.display(boolean=True, description="معتبر است")
    def is_currently_valid(self, obj):
        return obj.is_valid()


admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(User, CustomUserAdmin)

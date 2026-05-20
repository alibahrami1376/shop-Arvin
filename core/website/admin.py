from django.contrib import admin

from website.models import (
    ContactModel,
    ContactPageSettings,
    FAQItem,
    HomeBanner,
    LegalPage,
    SiteBrandingSettings,
    SiteWideSocialSettings,
)


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "sort_order",
        "is_default",
        "is_active",
        "created_date",
    )
    list_filter = ("is_active", "is_default")
    search_fields = ("title", "subtitle", "link")
    ordering = ("sort_order", "-created_date")


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "sort_order", "is_published", "created_date")
    list_filter = ("is_published",)
    search_fields = ("question", "answer")
    ordering = ("sort_order", "-created_date")


@admin.register(SiteBrandingSettings)
class SiteBrandingSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteBrandingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteWideSocialSettings)
class SiteWideSocialSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteWideSocialSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ("page_type", "title", "updated_date")
    readonly_fields = ("page_type",)


@admin.register(ContactPageSettings)
class ContactPageSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ContactPageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "phone_number",
        "subject",
        "content",
        "is_seen",
        "created_date",

    )

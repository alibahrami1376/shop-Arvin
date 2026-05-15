from django.contrib import admin

from website.models import ContactModel, FAQItem, HomeBanner


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "sort_order", "is_active", "created_date")
    list_filter = ("is_active",)
    search_fields = ("title", "link")
    ordering = ("sort_order", "-created_date")


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "sort_order", "is_published", "created_date")
    list_filter = ("is_published",)
    search_fields = ("question", "answer")
    ordering = ("sort_order", "-created_date")


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

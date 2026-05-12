from django.contrib import admin
from blog.models import Post, Category
from django_ckeditor_5.widgets import CKEditor5Widget
from django.db import models



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget},
    }

    date_hierarchy = "created_date"
    empty_value_display = "-خالی-"
    list_display = ("title", "author", "counted_view", "status", "published_date", "created_date")
    list_filter = ("status", "category", "created_date")
    search_fields = ["title", "content"]
    filter_horizontal = ("category",)
    list_editable = ("status",)
    readonly_fields = ("counted_view", "created_date", "updated_date")
    
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("title", "author", "image", "url")
        }),
        ("محتوا", {
            "fields": ("content",)
        }),
        ("دسته‌بندی و وضعیت", {
            "fields": ("category", "status", "published_date")
        }),
        ("آمار و تاریخ", {
            "fields": ("counted_view", "created_date", "updated_date"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


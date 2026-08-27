from django import forms
from django.contrib import admin
from django_ckeditor_5.widgets import CKEditor5Widget

from blog.models import Category, Post, PostImageModel, Tag


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            "content": CKEditor5Widget(config_name="extends"),
        }


class PostImageInline(admin.TabularInline):
    model = PostImageModel
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    inlines = (PostImageInline,)

    date_hierarchy = "created_date"
    empty_value_display = "-خالی-"
    list_display = (
        "title",
        "slug",
        "author",
        "counted_view",
        "status",
        "published_date",
        "created_date",
    )
    list_filter = ("status", "category", "tags", "created_date")
    search_fields = ["title", "slug", "content"]
    filter_horizontal = ("category", "tags")
    list_editable = ("status",)
    readonly_fields = ("counted_view", "created_date", "updated_date")

    fieldsets = (
        (
            "اطلاعات اصلی",
            {"fields": ("title", "slug", "author", "image", "url")},
        ),
        ("محتوا", {"fields": ("content",)}),
        (
            "دسته‌بندی، تگ و وضعیت",
            {"fields": ("category", "tags", "status", "published_date")},
        ),
        (
            "آمار و تاریخ",
            {
                "fields": ("counted_view", "created_date", "updated_date"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(PostImageModel)
class PostImageModelAdmin(admin.ModelAdmin):
    list_display = ("post", "file", "created_date")
    list_filter = ("created_date",)
    search_fields = ("post__title",)
    autocomplete_fields = ("post",)

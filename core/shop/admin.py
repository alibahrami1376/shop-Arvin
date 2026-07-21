from django.contrib import admin
from .models import ProductModel, ProductImageModel, ProductCategoryModel, ProductTagModel, WishlistProductModel

# Register your models here.

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "stock", "status","price","discount_percent", "created_date")
    filter_horizontal = ("category", "tags")

@admin.register(ProductCategoryModel)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "parent", "created_date")
    list_filter = ("parent",)

@admin.register(ProductTagModel)
class ProductTagModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug", "created_date")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created_date")

@admin.register(WishlistProductModel)
class WishlistProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")

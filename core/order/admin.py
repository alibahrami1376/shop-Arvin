from django.contrib import admin
from .models import (
    CheckoutPricingSettings,
    City,
    CouponModel,
    OrderItemModel,
    OrderModel,
    Province,
    UserAddressModel,
)

# Register your models here.


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("sort_order", "name")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "province", "is_active", "sort_order")
    list_filter = ("province", "is_active")
    search_fields = ("name", "province__name")
    autocomplete_fields = ("province",)
    ordering = ("province__name", "sort_order", "name")


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tracking_code",
        "user",
        "shipping_method",
        "city",
        "total_price",
        "discount_amount",
        "shipping_amount",
        "tax_amount",
        "coupon",
        "status",
        "created_date",
    )
    search_fields = ("tracking_code", "user__email")
    readonly_fields = ("tracking_code",)


@admin.register(OrderItemModel)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "created_date"
    )


@admin.register(CouponModel)
class CouponModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_limit_usage",
        "used_by_count",
        "expiration_date",
        "created_date"
    )
    
    def used_by_count(self, obj):
        return obj.used_by.all().count()


@admin.register(CheckoutPricingSettings)
class CheckoutPricingSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "shipping_enabled",
        "shipping_tehran_amount",
        "shipping_province_amount",
        "tax_enabled",
        "tax_percent",
        "updated_date",
    )

    def has_add_permission(self, request):
        return not CheckoutPricingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserAddressModel)
class UserAddressModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "state",
        "city",
        "zip_code",
        "created_date"
    )
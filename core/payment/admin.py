from django.contrib import admin

from .models import (
    BaleBotSettings,
    CardToCardSettings,
    PaymentMethodSettings,
    PaymentModel,
)


@admin.register(CardToCardSettings)
class CardToCardSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "bank_name", "account_holder", "updated_date")
    fieldsets = (
        (
            "اطلاعات حساب",
            {
                "fields": (
                    "bank_name",
                    "account_holder",
                    "card_number",
                    "iban",
                    "note",
                )
            },
        ),
        (
            "ارسال رسید",
            {
                "fields": (
                    ("telegram_enabled", "telegram_link"),
                    ("bale_enabled", "bale_link"),
                    ("rubika_enabled", "rubika_link"),
                    ("whatsapp_enabled", "whatsapp_link"),
                    ("email_enabled", "email_link"),
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not CardToCardSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BaleBotSettings)
class BaleBotSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "bot_username", "updated_date")
    fields = (
        "bot_token",
        "provider_token",
        "bot_username",
        "webhook_secret",
        "api_base",
        "deep_link_base",
        "link_token_ttl_minutes",
    )

    def has_add_permission(self, request):
        return not BaleBotSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PaymentMethodSettings)
class PaymentMethodSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gateway_enabled",
        "card_to_card_enabled",
        "bale_enabled",
        "updated_date",
    )
    fields = ("gateway_enabled", "card_to_card_enabled", "bale_enabled")

    def has_add_permission(self, request):
        return not PaymentMethodSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PaymentModel)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "method",
        "authority_id",
        "amount",
        "response_code",
        "status",
        "created_date",
    )
    list_filter = ("method", "status")
    search_fields = (
        "authority_id",
        "link_token",
        "bale_telegram_payment_charge_id",
        "bale_provider_payment_charge_id",
    )
    readonly_fields = (
        "link_token",
        "link_token_expires_at",
        "bale_chat_id",
        "bale_invoice_message_id",
        "bale_pre_checkout_id",
        "bale_telegram_payment_charge_id",
        "bale_provider_payment_charge_id",
    )

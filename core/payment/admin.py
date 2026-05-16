from django.contrib import admin

from .models import CardToCardSettings, PaymentModel


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
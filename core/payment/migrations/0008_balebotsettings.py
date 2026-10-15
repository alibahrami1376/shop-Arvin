from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0007_bale_wallet_payment"),
    ]

    operations = [
        migrations.CreateModel(
            name="BaleBotSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "bot_token",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="توکن بازو از BotFather بله",
                        max_length=255,
                        verbose_name="توکن ربات",
                    ),
                ),
                (
                    "provider_token",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="توکن پرداخت کیف‌پول؛ برای تست: WALLET-TEST-1111111111111111",
                        max_length=255,
                        verbose_name="توکن کیف‌پول (provider)",
                    ),
                ),
                (
                    "bot_username",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="بدون @ — برای دیپ‌لینک ble.ir",
                        max_length=128,
                        verbose_name="یوزرنیم ربات",
                    ),
                ),
                (
                    "webhook_secret",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="در URL وب‌هوک به‌صورت ?secret=... استفاده می‌شود",
                        max_length=255,
                        verbose_name="رمز وب‌هوک",
                    ),
                ),
                (
                    "api_base",
                    models.CharField(
                        blank=True,
                        default="https://tapi.bale.ai",
                        max_length=255,
                        verbose_name="آدرس پایه API",
                    ),
                ),
                (
                    "deep_link_base",
                    models.CharField(
                        blank=True,
                        default="https://ble.ir",
                        max_length=255,
                        verbose_name="پایه دیپ‌لینک",
                    ),
                ),
                (
                    "link_token_ttl_minutes",
                    models.PositiveIntegerField(
                        default=60,
                        verbose_name="اعتبار لینک پرداخت (دقیقه)",
                    ),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "تنظیمات ربات بله",
                "verbose_name_plural": "تنظیمات ربات بله",
            },
        ),
    ]

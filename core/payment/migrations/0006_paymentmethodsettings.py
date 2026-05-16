from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0005_cardtocardsettings_receipt_social"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentMethodSettings",
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
                    "gateway_enabled",
                    models.BooleanField(
                        default=True,
                        verbose_name="نمایش درگاه آنلاین (زرین‌پال)",
                    ),
                ),
                (
                    "card_to_card_enabled",
                    models.BooleanField(
                        default=True,
                        verbose_name="نمایش کارت به کارت",
                    ),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "تنظیمات روش‌های پرداخت",
                "verbose_name_plural": "تنظیمات روش‌های پرداخت",
            },
        ),
    ]

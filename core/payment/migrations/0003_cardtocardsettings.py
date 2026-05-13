from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0002_paymentmodel_method"),
    ]

    operations = [
        migrations.CreateModel(
            name="CardToCardSettings",
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
                    "bank_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="نام بانک"
                    ),
                ),
                (
                    "account_holder",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="نام صاحب حساب / کارت",
                    ),
                ),
                (
                    "card_number",
                    models.CharField(
                        blank=True, max_length=32, verbose_name="شماره کارت"
                    ),
                ),
                (
                    "iban",
                    models.CharField(
                        blank=True, max_length=34, verbose_name="شبا (IBAN)"
                    ),
                ),
                (
                    "note",
                    models.TextField(
                        blank=True,
                        help_text="مثلاً درخواست ارسال فیش یا شماره سفارش.",
                        verbose_name="متن راهنما برای مشتری",
                    ),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "تنظیمات کارت به کارت",
                "verbose_name_plural": "تنظیمات کارت به کارت",
            },
        ),
    ]

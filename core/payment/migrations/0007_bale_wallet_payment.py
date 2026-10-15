from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0006_paymentmethodsettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentmethodsettings",
            name="bale_enabled",
            field=models.BooleanField(
                default=False, verbose_name="نمایش پرداخت با بله"
            ),
        ),
        migrations.AlterField(
            model_name="paymentmodel",
            name="method",
            field=models.IntegerField(
                choices=[
                    (1, "درگاه آنلاین"),
                    (2, "کارت به کارت"),
                    (3, "پرداخت با بله"),
                ],
                default=1,
                verbose_name="روش پرداخت",
            ),
        ),
        migrations.AddField(
            model_name="paymentmodel",
            name="link_token",
            field=models.CharField(
                blank=True, db_index=True, max_length=64, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="paymentmodel",
            name="link_token_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentmodel",
            name="bale_chat_id",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="paymentmodel",
            name="bale_invoice_message_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentmodel",
            name="bale_pre_checkout_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="paymentmodel",
            name="bale_telegram_payment_charge_id",
            field=models.CharField(
                blank=True, max_length=255, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="paymentmodel",
            name="bale_provider_payment_charge_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

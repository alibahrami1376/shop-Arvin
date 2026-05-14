from django.db import migrations, models


def remap_old_failed_to_payment_failed(apps, schema_editor):
    PaymentModel = apps.get_model("payment", "PaymentModel")
    PaymentModel.objects.filter(status=3).update(status=4)


def remap_payment_failed_back_to_legacy_failed(apps, schema_editor):
    PaymentModel = apps.get_model("payment", "PaymentModel")
    # Legacy schema used 3 for failed; only rows that are payment_failed under new enum.
    PaymentModel.objects.filter(status=4).update(status=3)


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0003_cardtocardsettings"),
    ]

    operations = [
        migrations.RunPython(
            remap_old_failed_to_payment_failed,
            remap_payment_failed_back_to_legacy_failed,
        ),
        migrations.AlterField(
            model_name="paymentmodel",
            name="status",
            field=models.IntegerField(
                choices=[
                    (1, "در انتظار پرداخت"),
                    (2, "در حال آماده‌سازی"),
                    (3, "ارسال شده"),
                    (4, "پرداخت ناموفق"),
                    (5, "لغو شده"),
                ],
                default=1,
            ),
        ),
    ]

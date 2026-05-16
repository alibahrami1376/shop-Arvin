from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0004_payment_status_stages"),
    ]

    operations = [
        migrations.AddField(
            model_name="cardtocardsettings",
            name="telegram_enabled",
            field=models.BooleanField(default=False, verbose_name="فعال — تلگرام"),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="telegram_link",
            field=models.CharField(
                blank=True,
                help_text="مثال: https://t.me/username",
                max_length=500,
                verbose_name="لینک تلگرام",
            ),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="bale_enabled",
            field=models.BooleanField(default=False, verbose_name="فعال — بله"),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="bale_link",
            field=models.CharField(
                blank=True,
                help_text="مثال: https://ble.ir/username",
                max_length=500,
                verbose_name="لینک بله",
            ),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="rubika_enabled",
            field=models.BooleanField(default=False, verbose_name="فعال — روبیکا"),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="rubika_link",
            field=models.CharField(blank=True, max_length=500, verbose_name="لینک روبیکا"),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="whatsapp_enabled",
            field=models.BooleanField(default=False, verbose_name="فعال — واتساپ"),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="whatsapp_link",
            field=models.CharField(
                blank=True,
                help_text="لینک کامل یا شماره موبایل (مثال: 989121234567)",
                max_length=500,
                verbose_name="لینک واتساپ",
            ),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="email_enabled",
            field=models.BooleanField(default=False, verbose_name="فعال — ایمیل"),
        ),
        migrations.AddField(
            model_name="cardtocardsettings",
            name="email_link",
            field=models.CharField(
                blank=True,
                help_text="آدرس ایمیل (مثال: shop@example.com)",
                max_length=500,
                verbose_name="ایمیل",
            ),
        ),
    ]

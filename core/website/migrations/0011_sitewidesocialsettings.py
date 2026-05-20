from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0010_sitebrandingsettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteWideSocialSettings",
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
                    "instagram_link",
                    models.CharField(
                        blank=True, max_length=500, verbose_name="لینک اینستاگرام"
                    ),
                ),
                (
                    "telegram_link",
                    models.CharField(
                        blank=True, max_length=500, verbose_name="لینک تلگرام"
                    ),
                ),
                (
                    "linkedin_link",
                    models.CharField(
                        blank=True, max_length=500, verbose_name="لینک لینکدین"
                    ),
                ),
                (
                    "bale_link",
                    models.CharField(
                        blank=True,
                        help_text="مثال: https://ble.ir/username",
                        max_length=500,
                        verbose_name="لینک بله",
                    ),
                ),
                (
                    "rubika_link",
                    models.CharField(
                        blank=True, max_length=500, verbose_name="لینک روبیکا"
                    ),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "شبکه‌های اجتماعی سایت",
                "verbose_name_plural": "شبکه‌های اجتماعی سایت",
            },
        ),
    ]

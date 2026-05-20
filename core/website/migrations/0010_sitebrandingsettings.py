from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0009_legal_and_contact_settings"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteBrandingSettings",
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
                    "logo",
                    models.ImageField(
                        blank=True,
                        help_text="PNG یا WEBP — دقیقاً 200×222 پیکسل.",
                        null=True,
                        upload_to="branding/",
                        verbose_name="لوگوی سایت",
                    ),
                ),
                (
                    "site_name",
                    models.CharField(
                        blank=True,
                        default="فروشگاه آروین",
                        max_length=120,
                        verbose_name="نام فروشگاه (متن alt لوگو)",
                    ),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "لوگوی سایت",
                "verbose_name_plural": "لوگوی سایت",
            },
        ),
    ]

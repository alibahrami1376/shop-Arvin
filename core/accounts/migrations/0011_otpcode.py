from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_remove_otp_sms_phone_verified"),
    ]

    operations = [
        migrations.CreateModel(
            name="OTPCode",
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
                ("mobile", models.CharField(max_length=11, verbose_name="موبایل")),
                ("code", models.CharField(max_length=6, verbose_name="کد")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "is_used",
                    models.BooleanField(default=False, verbose_name="استفاده شده"),
                ),
            ],
            options={
                "verbose_name": "کد OTP",
                "verbose_name_plural": "کدهای OTP",
                "ordering": ["-created_at"],
            },
        ),
    ]

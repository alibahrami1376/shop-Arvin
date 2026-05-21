# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_meta_verbose"),
    ]

    operations = [
        migrations.CreateModel(
            name="SMSSettings",
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
                    "sms_enabled",
                    models.BooleanField(
                        default=True,
                        help_text="در صورت غیرفعال، ارسال از طریق کاوه‌نگار انجام نمی‌شود و ثبت‌نام/تأیید موبایل با OTP عملاً متوقف می‌شود.",
                        verbose_name="ارسال پیامک OTP فعال است",
                    ),
                ),
                (
                    "updated_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="آخرین به‌روزرسانی"
                    ),
                ),
            ],
            options={
                "verbose_name": "تنظیمات پیامک (OTP)",
                "verbose_name_plural": "تنظیمات پیامک (OTP)",
            },
        ),
    ]

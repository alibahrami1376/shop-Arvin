import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0011_otpcode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(
                default=False,
                help_text="با تأیید پیامک (ثبت‌نام موبایل) یا تأیید ایمیل True می‌شود.",
                verbose_name="حساب تأیید شده",
            ),
        ),
        migrations.AddField(
            model_name="otpcode",
            name="user",
            field=models.ForeignKey(
                blank=True,
                help_text="در ثبت‌نام اولیه هنوز کاربر ساخته نشده؛ بعد از تأیید موفق به کاربر وصل می‌شود.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="otp_codes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="کاربر",
            ),
        ),
    ]

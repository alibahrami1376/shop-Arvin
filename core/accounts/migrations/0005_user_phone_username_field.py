# شناسه ورود = موبایل؛ حذف قید «ایمیل یا موبایل»

from django.db import migrations, models

import accounts.validators


def ensure_phone_before_not_null(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    missing = User.objects.filter(phone_number__isnull=True)
    if missing.exists():
        raise RuntimeError(
            "قبل از migrate، برای همه کاربران بدون موبایل شماره ثبت کنید "
            f"(تعداد: {missing.count()})."
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_smssettings"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="user",
            name="accounts_user_email_or_phone_required",
        ),
        migrations.RunPython(ensure_phone_before_not_null, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                max_length=11,
                unique=True,
                validators=[accounts.validators.validate_iranian_cellphone_number],
                verbose_name="شماره موبایل",
                help_text="شناسه ورود و ثبت‌نام",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True,
                help_text="اختیاری؛ برای ارتباط یا حساب‌های ادمین",
                max_length=254,
                null=True,
                unique=True,
                verbose_name="ایمیل",
            ),
        ),
    ]

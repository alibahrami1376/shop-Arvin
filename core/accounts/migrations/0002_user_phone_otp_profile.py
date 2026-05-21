# دستی: انتقال phone از Profile به User، ایمیل اختیاری، مدل OTP

import accounts.validators
from django.db import migrations, models
from django.db.models import Q


def copy_profile_phone_to_user(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    for profile in Profile.objects.select_related("user").iterator():
        if profile.phone_number:
            user = profile.user
            user.phone_number = profile.phone_number
            # داده مهاجرت‌شده از پروفایل قدیمی؛ کاربران موجود بدون اجبار OTP
            user.phone_verified = True
            user.save(update_fields=["phone_number", "phone_verified"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone_verified",
            field=models.BooleanField(
                default=False, verbose_name="موبایل تأیید شده"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=11,
                null=True,
                validators=[accounts.validators.validate_iranian_cellphone_number],
                verbose_name="شماره موبایل",
            ),
        ),
        migrations.RunPython(copy_profile_phone_to_user, noop_reverse),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True,
                max_length=254,
                null=True,
                unique=True,
                verbose_name="ایمیل",
            ),
        ),
        migrations.RemoveField(
            model_name="profile",
            name="phone_number",
        ),
        migrations.AlterField(
            model_name="profile",
            name="first_name",
            field=models.CharField(blank=True, max_length=255, verbose_name="نام"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="last_name",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="نام خانوادگی"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=11,
                null=True,
                unique=True,
                validators=[accounts.validators.validate_iranian_cellphone_number],
                verbose_name="شماره موبایل",
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                check=Q(email__isnull=False) | Q(phone_number__isnull=False),
                name="accounts_user_email_or_phone_required",
            ),
        ),
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
                (
                    "mobile",
                    models.CharField(max_length=11, verbose_name="موبایل"),
                ),
                ("code", models.CharField(max_length=6, verbose_name="کد")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
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

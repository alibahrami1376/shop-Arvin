# سوپریوزر با ایمیل؛ موبایل اختیاری برای ادمین

from django.db import migrations, models
from django.db.models import Q

import accounts.validators


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_user_phone_username_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True,
                help_text="شناسه ورود ادمین و سوپریوزر",
                max_length=254,
                null=True,
                unique=True,
                verbose_name="ایمیل",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                help_text="شناسه ورود و ثبت‌نام مشتری",
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
    ]

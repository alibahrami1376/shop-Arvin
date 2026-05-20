import django_ckeditor_5.fields
from django.db import migrations, models


def seed_legal_pages(apps, schema_editor):
    LegalPage = apps.get_model("website", "LegalPage")
    defaults = [
        (
            "privacy",
            "حریم خصوصی",
            "<p>در این بخش می‌توانید سیاست حفظ حریم خصوصی فروشگاه را شرح دهید. متن را از پنل مدیریت ویرایش کنید.</p>",
        ),
        (
            "terms",
            "قوانین و مقررات",
            "<p>در این بخش می‌توانید قوانین و مقررات استفاده از فروشگاه را شرح دهید. متن را از پنل مدیریت ویرایش کنید.</p>",
        ),
    ]
    for page_type, title, content in defaults:
        LegalPage.objects.get_or_create(
            page_type=page_type,
            defaults={"title": title, "content": content},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0008_homebanner_display_target"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactPageSettings",
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
                    "email",
                    models.EmailField(
                        blank=True,
                        default="info@truckparts.ir",
                        max_length=254,
                        verbose_name="ایمیل",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        default="۰۲۱-۱۲۳۴۵۶۷۸",
                        max_length=50,
                        verbose_name="تلفن",
                    ),
                ),
                (
                    "working_hours",
                    models.CharField(
                        blank=True,
                        default="شنبه تا پنجشنبه: ۹ صبح تا ۶ عصر",
                        max_length=255,
                        verbose_name="ساعات کاری",
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
                (
                    "bale_channel_link",
                    models.CharField(
                        blank=True, max_length=500, verbose_name="لینک کانال بله"
                    ),
                ),
                (
                    "bale_channel_text",
                    models.CharField(
                        blank=True,
                        help_text="جمله‌ای که زیر لینک کانال نمایش داده می‌شود.",
                        max_length=500,
                        verbose_name="متن معرفی کانال بله",
                    ),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "تنظیمات تماس با ما",
                "verbose_name_plural": "تنظیمات تماس با ما",
            },
        ),
        migrations.CreateModel(
            name="LegalPage",
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
                    "page_type",
                    models.CharField(
                        choices=[
                            ("privacy", "حریم خصوصی"),
                            ("terms", "قوانین و مقررات"),
                        ],
                        max_length=20,
                        unique=True,
                        verbose_name="نوع صفحه",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="عنوان")),
                (
                    "content",
                    django_ckeditor_5.fields.CKEditor5Field(verbose_name="محتوا"),
                ),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "صفحه قانونی",
                "verbose_name_plural": "صفحات قانونی",
            },
        ),
        migrations.RunPython(seed_legal_pages, migrations.RunPython.noop),
    ]

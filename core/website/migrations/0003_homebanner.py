from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0002_faqitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeBanner",
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
                ("title", models.CharField(max_length=200, verbose_name="عنوان (alt)")),
                (
                    "image",
                    models.FileField(
                        help_text="فرمت‌های JPG، PNG، WEBP و GIF — ابعاد پیشنهادی ۱۹۲۰×۶۰۰",
                        upload_to="banners/home/",
                        verbose_name="تصویر یا GIF",
                    ),
                ),
                (
                    "link",
                    models.CharField(
                        blank=True,
                        help_text="مثال: /shop/ یا آدرس کامل",
                        max_length=500,
                        verbose_name="لینک کلیک (اختیاری)",
                    ),
                ),
                (
                    "sort_order",
                    models.PositiveIntegerField(
                        default=0, verbose_name="ترتیب نمایش"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="فعال"),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "بنر صفحه اصلی",
                "verbose_name_plural": "بنرهای صفحه اصلی",
                "ordering": ["sort_order", "-created_date"],
            },
        ),
    ]

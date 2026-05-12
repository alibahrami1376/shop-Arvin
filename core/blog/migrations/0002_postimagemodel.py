import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostImageModel",
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
                    "file",
                    models.ImageField(
                        upload_to="blog/extra-img/",
                        verbose_name="فایل تصویر",
                    ),
                ),
                (
                    "created_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="تاریخ ایجاد",
                    ),
                ),
                (
                    "updated_date",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="تاریخ بروزرسانی",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_images",
                        to="blog.post",
                        verbose_name="پست",
                    ),
                ),
            ],
            options={
                "verbose_name": "تصویر پست",
                "verbose_name_plural": "تصاویر پست",
                "ordering": ["created_date"],
            },
        ),
    ]

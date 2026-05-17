from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0007_alter_homebanner_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="homebanner",
            name="display_target",
            field=models.CharField(
                choices=[
                    ("all", "همه دستگاه‌ها"),
                    ("mobile", "فقط موبایل"),
                    ("desktop", "فقط دسکتاپ"),
                ],
                default="all",
                max_length=10,
                verbose_name="دستگاه نمایش",
            ),
        ),
    ]

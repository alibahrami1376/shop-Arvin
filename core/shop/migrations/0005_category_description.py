# Generated manually for category description field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0004_image_alt_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="productcategorymodel",
            name="description",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="توضیحات دسته",
            ),
        ),
    ]

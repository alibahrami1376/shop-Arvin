from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productcategorymodel",
            options={
                "ordering": ["title"],
                "verbose_name": "دسته‌بندی محصول",
                "verbose_name_plural": "دسته‌بندی‌های محصول",
            },
        ),
        migrations.AddField(
            model_name="productcategorymodel",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="shop.productcategorymodel",
                verbose_name="دسته والد",
            ),
        ),
    ]

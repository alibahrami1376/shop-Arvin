from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0004_seed_default_home_banners"),
    ]

    operations = [
        migrations.AddField(
            model_name="homebanner",
            name="subtitle",
            field=models.TextField(blank=True, verbose_name="متن توضیح"),
        ),
        migrations.AddField(
            model_name="homebanner",
            name="button_text",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="متن دکمه"
            ),
        ),
        migrations.AddField(
            model_name="homebanner",
            name="image_alt",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="متن alt تصویر"
            ),
        ),
        migrations.AddField(
            model_name="homebanner",
            name="background_style",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "سبک ۱"), (2, "سبک ۲"), (3, "سبک ۳")],
                default=1,
                verbose_name="سبک پس‌زمینه",
            ),
        ),
        migrations.AddField(
            model_name="homebanner",
            name="is_default",
            field=models.BooleanField(
                default=False,
                help_text="بنرهای پیش‌فرض فقط از پنل قابل فعال/غیرفعال شدن هستند.",
                verbose_name="بنر پیش‌فرض",
            ),
        ),
        migrations.AlterField(
            model_name="homebanner",
            name="link",
            field=models.CharField(
                blank=True,
                help_text="مثال: /shop/product/grid/",
                max_length=500,
                verbose_name="لینک دکمه",
            ),
        ),
        migrations.AlterField(
            model_name="homebanner",
            name="title",
            field=models.CharField(max_length=200, verbose_name="عنوان"),
        ),
    ]

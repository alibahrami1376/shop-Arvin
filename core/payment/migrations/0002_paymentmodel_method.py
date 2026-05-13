# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentmodel",
            name="method",
            field=models.IntegerField(
                choices=[(1, "درگاه آنلاین"), (2, "کارت به کارت")],
                default=1,
                verbose_name="روش پرداخت",
            ),
        ),
    ]

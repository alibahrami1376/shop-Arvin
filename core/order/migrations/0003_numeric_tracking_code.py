import secrets

from django.db import migrations, models

TRACKING_CODE_MIN_LENGTH = 5
TRACKING_CODE_MAX_LENGTH = 7


def _generate_tracking_code():
    length = secrets.choice(
        range(TRACKING_CODE_MIN_LENGTH, TRACKING_CODE_MAX_LENGTH + 1)
    )
    first = secrets.choice("123456789")
    rest = "".join(secrets.choice("0123456789") for _ in range(length - 1))
    return first + rest


def regenerate_numeric_tracking_codes(apps, schema_editor):
    OrderModel = apps.get_model("order", "OrderModel")
    used = set()
    for order in OrderModel.objects.all().order_by("pk"):
        for _ in range(64):
            code = _generate_tracking_code()
            if code not in used:
                order.tracking_code = code
                order.save(update_fields=["tracking_code"])
                used.add(code)
                break
        else:
            raise RuntimeError(
                f"Could not generate tracking code for order {order.pk}"
            )


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0002_ordermodel_tracking_code"),
    ]

    operations = [
        migrations.RunPython(
            regenerate_numeric_tracking_codes,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="ordermodel",
            name="tracking_code",
            field=models.CharField(
                editable=False,
                max_length=7,
                unique=True,
                verbose_name="کد سفارش",
            ),
        ),
    ]

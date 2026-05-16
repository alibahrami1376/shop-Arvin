import secrets

from django.db import migrations, models

TRACKING_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
TRACKING_CODE_PREFIX = "ARV-"


def _generate_tracking_code():
    suffix = "".join(
        secrets.choice(TRACKING_CODE_ALPHABET) for _ in range(8)
    )
    return f"{TRACKING_CODE_PREFIX}{suffix}"


def populate_tracking_codes(apps, schema_editor):
    OrderModel = apps.get_model("order", "OrderModel")
    used = set(
        OrderModel.objects.exclude(tracking_code__isnull=True)
        .exclude(tracking_code="")
        .values_list("tracking_code", flat=True)
    )
    for order in OrderModel.objects.filter(tracking_code__isnull=True):
        for _ in range(32):
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
        ("order", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordermodel",
            name="tracking_code",
            field=models.CharField(
                editable=False,
                max_length=16,
                null=True,
                unique=True,
                verbose_name="کد پیگیری",
            ),
        ),
        migrations.RunPython(populate_tracking_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="ordermodel",
            name="tracking_code",
            field=models.CharField(
                editable=False,
                max_length=16,
                unique=True,
                verbose_name="کد پیگیری",
            ),
        ),
    ]

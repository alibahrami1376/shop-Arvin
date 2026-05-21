# همگام‌سازی sequenceهای id پس از import/restore دیتا

from django.db import migrations


def reset_sequences(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    from accounts.db_utils import reset_pg_id_sequences

    reset_pg_id_sequences()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_merge_20260520_1709"),
    ]

    operations = [
        migrations.RunPython(reset_sequences, migrations.RunPython.noop),
    ]

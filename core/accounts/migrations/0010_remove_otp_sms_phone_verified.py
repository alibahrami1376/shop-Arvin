from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_alter_smssettings_sms_enabled_alter_user_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="phone_verified",
        ),
        migrations.DeleteModel(
            name="OTPCode",
        ),
        migrations.DeleteModel(
            name="SMSSettings",
        ),
    ]

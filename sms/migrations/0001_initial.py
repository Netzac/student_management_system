from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SMSLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recipient_phone", models.CharField(blank=True, max_length=20)),
                ("recipient_name", models.CharField(blank=True, max_length=100)),
                ("message", models.TextField()),
                ("status", models.CharField(choices=[("sent", "Sent"), ("failed", "Failed"), ("skipped", "Skipped")], max_length=10)),
                ("trigger", models.CharField(choices=[("fee_payment", "Fee Payment"), ("bulk_sms", "Bulk SMS"), ("manual", "Manual")], max_length=20)),
                ("twilio_sid", models.CharField(blank=True, max_length=50)),
                ("error_message", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("sent_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sms_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "SMS Log",
                "verbose_name_plural": "SMS Logs",
                "ordering": ["-created_at"],
                "permissions": [("can_send_bulk_sms", "Can send bulk SMS")],
            },
        ),
    ]

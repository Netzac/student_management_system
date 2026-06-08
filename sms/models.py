from django.conf import settings
from django.db import models


class SMSLog(models.Model):
    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("skipped", "Skipped"),
    ]
    TRIGGER_CHOICES = [
        ("fee_payment", "Fee Payment"),
        ("bulk_sms", "Bulk SMS"),
        ("manual", "Manual"),
    ]

    recipient_phone = models.CharField(max_length=20, blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    twilio_sid = models.CharField(max_length=50, blank=True)
    error_message = models.CharField(max_length=500, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sms_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "SMS Log"
        verbose_name_plural = "SMS Logs"
        permissions = [
            ("can_send_bulk_sms", "Can send bulk SMS"),
        ]

    def __str__(self):
        return (
            f"{self.trigger} → {self.recipient_phone} [{self.status}] "
            f"{self.created_at:%Y-%m-%d %H:%M}"
        )

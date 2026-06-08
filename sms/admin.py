from django.contrib import admin

from .models import SMSLog


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = (
        "recipient_phone",
        "recipient_name",
        "status",
        "trigger",
        "twilio_sid",
        "error_message",
        "created_at",
    )
    list_filter = ("status", "trigger", "created_at")
    search_fields = ("recipient_phone", "recipient_name", "message")
    readonly_fields = ("created_at",)

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from sms.models import SMSLog
from sms.services import normalize_phone, send_sms

from .models import InvoiceItem, Receipt

logger = logging.getLogger(__name__)


def _get_fee_type(invoice):
    item = InvoiceItem.objects.filter(invoice=invoice).select_related("feetype").first()
    if item and item.feetype:
        return str(item.feetype)
    return "School Fees"


@receiver(post_save, sender=Receipt)
def send_fee_payment_sms(sender, instance, created, **kwargs):
    """Send SMS to parent/guardian after a new fee payment is recorded."""
    if not created:
        return

    invoice = instance.invoice
    student = invoice.student
    guardian_phone = student.parent_contact_number
    guardian_name = (
        f"{student.parent_first_name} {student.parent_last_name}".strip() or "Guardian"
    )
    student_name = str(student)
    amount = instance.amount_paid
    fee_type = _get_fee_type(invoice)
    receipt_number = instance.pk
    outstanding = invoice.balance()
    school_name = settings.SCHOOL_NAME

    if not guardian_phone:
        logger.warning("No guardian phone for student %s, skipping SMS", student_name)
        SMSLog.objects.create(
            recipient_phone="",
            recipient_name=guardian_name,
            message="[skipped — no phone number]",
            status="skipped",
            trigger="fee_payment",
        )
        return

    message = (
        f"Dear {guardian_name}, payment of {amount} for {student_name} "
        f"({fee_type}) received. Receipt: {receipt_number}. "
        f"Balance: {outstanding}. Thank you. - {school_name}"
    )

    result = send_sms(guardian_phone, message, recipient_name=guardian_name)
    normalized = normalize_phone(guardian_phone) or guardian_phone

    SMSLog.objects.create(
        recipient_phone=normalized,
        recipient_name=guardian_name,
        message=message,
        status="sent" if result["success"] else "failed",
        trigger="fee_payment",
        twilio_sid=result.get("sid") or "",
        error_message=result.get("error") or "",
    )

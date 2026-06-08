import logging
import re
import time
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    phonenumbers = None


def normalize_phone(phone: str, default_country_code: str = None) -> Optional[str]:
    """
    Normalize a phone number to E.164 format (+[country_code][number]).
    """
    if not phone:
        return None

    if default_country_code is None:
        default_country_code = getattr(settings, "DEFAULT_COUNTRY_CODE", "233")

    cleaned = re.sub(r"[\s\-\(\)]", "", str(phone).strip())
    if not cleaned:
        return None

    if phonenumbers is not None:
        try:
            if cleaned.startswith("+"):
                parsed = phonenumbers.parse(cleaned, None)
            else:
                parsed = phonenumbers.parse(cleaned, default_country_code)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
        except phonenumbers.NumberParseException:
            pass

    if cleaned.startswith("+"):
        digits = cleaned[1:]
        if digits.isdigit() and len(digits) >= 7:
            return f"+{digits}"
        return None

    if cleaned.startswith("00"):
        digits = cleaned[2:]
        if digits.isdigit() and len(digits) >= 7:
            return f"+{digits}"
        return None

    if cleaned.startswith("0"):
        digits = cleaned[1:]
        if digits.isdigit() and len(digits) >= 7:
            return f"+{default_country_code}{digits}"
        return None

    if cleaned.isdigit():
        if len(cleaned) >= 10:
            return f"+{cleaned}"
        if len(cleaned) >= 7:
            return f"+{default_country_code}{cleaned}"

    return None


def send_sms(phone_number: str, message: str, recipient_name: str = "") -> dict:
    """
    Send a single SMS via Twilio. Never raises — failures return a dict.
    """
    normalized = normalize_phone(phone_number)
    if not normalized:
        error = f"Invalid phone number: {phone_number}"
        logger.warning(error)
        return {"success": False, "sid": None, "error": error}

    if not getattr(settings, "SMS_ENABLED", False):
        logger.warning("SMS disabled — not sending to %s", normalized)
        return {"success": False, "sid": None, "error": "SMS disabled"}

    if getattr(settings, "SMS_USE_SANDBOX", True):
        logger.info(
            "[SMS SANDBOX] To: %s (%s) | Message: %s",
            normalized,
            recipient_name or "recipient",
            message,
        )
        return {"success": True, "sid": "SANDBOX", "error": None}

    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        twilio_message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=normalized,
        )
        logger.info("SMS sent to %s, SID: %s", normalized, twilio_message.sid)
        return {"success": True, "sid": twilio_message.sid, "error": None}
    except ImportError as e:
        logger.error("Twilio package not installed: %s", e)
        return {"success": False, "sid": None, "error": "Twilio package not installed"}
    except Exception as e:
        if type(e).__name__ == "TwilioRestException":
            logger.error("Twilio error sending to %s: %s", normalized, e)
        else:
            logger.error("SMS error sending to %s: %s", normalized, e)
        return {"success": False, "sid": None, "error": str(e)}


def send_bulk_sms(recipients: list, message: str, sent_by=None) -> dict:
    """
    Send SMS to multiple recipients and log each attempt to SMSLog.
    """
    from .models import SMSLog

    summary = {
        "total": len(recipients),
        "sent": 0,
        "failed": 0,
        "skipped": 0,
        "failures": [],
    }

    for i, recipient in enumerate(recipients):
        phone = recipient.get("phone", "")
        name = recipient.get("name", "")

        if not phone:
            summary["skipped"] += 1
            SMSLog.objects.create(
                recipient_phone="",
                recipient_name=name,
                message=message,
                status="skipped",
                trigger="bulk_sms",
                error_message="No phone number",
                sent_by=sent_by,
            )
            continue

        result = send_sms(phone, message, recipient_name=name)
        normalized = normalize_phone(phone) or phone

        if result["success"]:
            summary["sent"] += 1
            status = "sent"
        else:
            summary["failed"] += 1
            status = "failed"
            summary["failures"].append(
                {"name": name, "phone": phone, "error": result.get("error", "")}
            )

        SMSLog.objects.create(
            recipient_phone=normalized,
            recipient_name=name,
            message=message,
            status=status,
            trigger="bulk_sms",
            twilio_sid=result.get("sid") or "",
            error_message=result.get("error") or "",
            sent_by=sent_by,
        )

        if i < len(recipients) - 1:
            time.sleep(0.1)

    return summary

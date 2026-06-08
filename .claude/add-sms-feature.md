# SMS Integration — Django School Management System
## Feature Prompt for Claude Code / Cursor / Codex
## Provider: Twilio (Global — 190+ countries)

---

## CONTEXT

This is a Django school management system **intended for global deployment** (starting in Ghana, expanding internationally). We are adding SMS notification capabilities using **Twilio** for:

1. **Automatic SMS** to a student's guardian after a fee payment is recorded
2. **Bulk SMS** — admin or teacher can send a custom SMS to all or selected guardians

The project uses:
- Django (latest stable) with Django ORM
- A `Student` model with a related `Guardian` or a `guardian_phone` field
- A `FeePayment` model (or similar) that records fee transactions
- A custom admin dashboard
- `.env` file for secrets (python-decouple or django-environ)

**Architecture principle:** Build a provider-agnostic SMS service layer so the SMS backend
(Twilio today, potentially others in future) can be swapped without touching business logic.

---

## DEPENDENCIES

```
twilio>=9.0.0     # Add to requirements.txt
```

---

## ENVIRONMENT VARIABLES (already in .env)

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+12015551234
SMS_ENABLED=True
SMS_USE_SANDBOX=True        # True = log to console only, no real SMS sent
SCHOOL_NAME=Your School Name
```

---

## TASK 1 — Django Settings Updates

In `settings.py` (reading from `.env` using python-decouple or django-environ):

```python
# SMS Configuration
SMS_ENABLED           = env.bool("SMS_ENABLED", default=False)
SMS_USE_SANDBOX       = env.bool("SMS_USE_SANDBOX", default=True)
TWILIO_ACCOUNT_SID    = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN     = env("TWILIO_AUTH_TOKEN", default="")
TWILIO_PHONE_NUMBER   = env("TWILIO_PHONE_NUMBER", default="")
SCHOOL_NAME           = env("SCHOOL_NAME", default="Our School")
```

If using `python-decouple`, use `config("KEY", default=..., cast=bool)` pattern.

---

## TASK 2 — Create the SMS Service Layer

Create `sms/services.py` with a **provider-agnostic interface** backed by Twilio.

### 2a. Phone number normalizer

```python
def normalize_phone(phone: str, default_country_code: str = "233") -> str | None:
    """
    Normalize a phone number to E.164 format (+[country_code][number]).
    - If already in E.164 (starts with +), return as-is after stripping spaces/dashes
    - If starts with 0 (local format like 0241234567), prepend default_country_code
    - If starts with 00, replace with +
    - Return None if the number appears invalid (too short, non-numeric after stripping)
    """
```

### 2b. Single SMS sender

```python
def send_sms(phone_number: str, message: str, recipient_name: str = "") -> dict:
    """
    Send a single SMS via Twilio.
    
    - Normalize phone_number to E.164 first
    - If SMS_USE_SANDBOX=True: log the message to Django logger (INFO level), return success
    - If SMS_ENABLED=False: log warning, return {"success": False, "error": "SMS disabled"}
    - Use Twilio client: client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=phone)
    - On TwilioRestException: log the error, return {"success": False, "error": str(e)}
    - On any other exception: log the error, return {"success": False, "error": str(e)}
    - NEVER raise — SMS failure must not crash the calling code
    - Return: {"success": True/False, "sid": <twilio_sid or None>, "error": <str or None>}
    """
```

### 2c. Bulk SMS sender

```python
def send_bulk_sms(recipients: list[dict], message: str, sent_by=None) -> dict:
    """
    Send SMS to multiple recipients.
    
    recipients format: [{"phone": "+233241234567", "name": "John Doe"}, ...]
    
    - Loop through recipients, call send_sms() for each
    - Log each result to SMSLog model (see Task 3)
    - Return summary: {
        "total": N,
        "sent": N,
        "failed": N,
        "skipped": N,       # no phone number
        "failures": [{"name": ..., "phone": ..., "error": ...}]
      }
    - Add a 100ms delay between messages to respect Twilio rate limits (1 msg/sec on trial)
    """
```

---

## TASK 3 — SMSLog Model

Create `sms/models.py`:

```python
class SMSLog(models.Model):
    STATUS_CHOICES = [
        ("sent",    "Sent"),
        ("failed",  "Failed"),
        ("skipped", "Skipped"),
    ]
    TRIGGER_CHOICES = [
        ("fee_payment", "Fee Payment"),
        ("bulk_sms",    "Bulk SMS"),
        ("manual",      "Manual"),
    ]

    recipient_phone = models.CharField(max_length=20, blank=True)
    recipient_name  = models.CharField(max_length=100, blank=True)
    message         = models.TextField()
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES)
    trigger         = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    twilio_sid      = models.CharField(max_length=50, blank=True)   # Twilio message SID
    error_message   = models.CharField(max_length=500, blank=True)
    sent_by         = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          null=True, blank=True,
                          on_delete=models.SET_NULL,
                          related_name="sms_logs"
                      )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name     = "SMS Log"
        verbose_name_plural = "SMS Logs"

    def __str__(self):
        return f"{self.trigger} → {self.recipient_phone} [{self.status}] {self.created_at:%Y-%m-%d %H:%M}"
```

Register in `sms/admin.py` with list_display:
`recipient_phone, recipient_name, status, trigger, twilio_sid, error_message, created_at`

---

## TASK 4 — Auto SMS After Fee Payment (Django Signal)

Find the existing FeePayment model (likely in `fees/models.py`).

Create `fees/signals.py`:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=FeePayment)
def send_fee_payment_sms(sender, instance, created, **kwargs):
    """
    After a new FeePayment is saved, send an SMS to the student's guardian.
    Only fires on `created=True` (not on updates/edits).
    """
    if not created:
        return

    # --- Adjust field names below to match your actual FeePayment model ---
    student         = instance.student
    guardian_phone  = getattr(student, "guardian_phone", None) \
                   or getattr(getattr(student, "guardian", None), "phone", None)
    guardian_name   = getattr(student, "guardian_name", "") \
                   or getattr(getattr(student, "guardian", None), "name", "Guardian")
    student_name    = str(student)
    amount          = instance.amount
    fee_type        = getattr(instance, "fee_type", "School Fees")
    receipt_number  = getattr(instance, "receipt_number", instance.pk)
    # Outstanding balance — calculate or use field if available
    outstanding     = getattr(instance, "outstanding_balance", 0)
    school_name     = settings.SCHOOL_NAME

    if not guardian_phone:
        logger.warning(f"No guardian phone for student {student_name}, skipping SMS")
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

    SMSLog.objects.create(
        recipient_phone=guardian_phone,
        recipient_name=guardian_name,
        message=message,
        status="sent" if result["success"] else "failed",
        trigger="fee_payment",
        twilio_sid=result.get("sid", ""),
        error_message=result.get("error", ""),
    )
```

Register in `fees/apps.py`:

```python
class FeesConfig(AppConfig):
    name = "fees"

    def ready(self):
        import fees.signals  # noqa
```

---

## TASK 5 — Bulk SMS View

Create `sms/views.py` with `BulkSMSView`:

- Mixin: `LoginRequiredMixin`
- Permission check: `request.user.is_staff` or custom permission `sms.can_send_bulk_sms`
- URL: `dashboard/sms/bulk/`

### GET — render the bulk SMS form

Template: `sms/templates/sms/bulk_sms.html`

Form fields:
1. **Recipient group** (radio/select):
   - `all_guardians` — every guardian with a phone number
   - `by_class` — dropdown of class/grade choices from DB
   - `individual` — searchable multi-select of students
2. **Message** (textarea, 160-char soft limit with JS counter; warn if over)
3. **Preview** — JS live count of recipients before sending
4. **Send button**

Recent SMS history table at the bottom: last 20 `SMSLog` entries with `trigger="bulk_sms"`.

### POST — process and send

```python
def post(self, request):
    group     = request.POST.get("recipient_group")
    message   = request.POST.get("message", "").strip()

    # 1. Collect recipients based on group selection
    if group == "all_guardians":
        recipients = build_all_guardian_recipients()      # helper — see below
    elif group == "by_class":
        class_id   = request.POST.get("class_id")
        recipients = build_class_recipients(class_id)
    elif group == "individual":
        student_ids = request.POST.getlist("student_ids")
        recipients  = build_individual_recipients(student_ids)
    else:
        messages.error(request, "Invalid recipient group.")
        return redirect("bulk-sms")

    # 2. Send
    result = send_bulk_sms(recipients, message, sent_by=request.user)

    # 3. Log and redirect to results
    messages.success(request,
        f"SMS sent: {result['sent']} delivered, {result['failed']} failed, {result['skipped']} skipped."
    )
    return redirect("bulk-sms")
```

Helper functions (in `sms/views.py` or `sms/utils.py`):

```python
def build_all_guardian_recipients():
    # Query all students with a non-empty guardian phone
    # Return: [{"phone": "...", "name": "..."}, ...]

def build_class_recipients(class_id):
    # Filter students by class/grade, return same format

def build_individual_recipients(student_id_list):
    # Filter by PK list, return same format
```

---

## TASK 6 — SMS App Setup

Create the `sms` Django app if it doesn't exist:

```bash
python manage.py startapp sms
```

Add to `INSTALLED_APPS` in `settings.py`:
```python
"sms",
```

Create `sms/urls.py`:
```python
from django.urls import path
from .views import BulkSMSView, SMSLogListView

urlpatterns = [
    path("bulk/",  BulkSMSView.as_view(),    name="bulk-sms"),
    path("logs/",  SMSLogListView.as_view(),  name="sms-logs"),
]
```

Include in main or dashboard `urls.py`:
```python
path("dashboard/sms/", include("sms.urls")),
```

---

## TASK 7 — Migrations

```bash
python manage.py makemigrations sms
python manage.py migrate
```

---

## TASK 8 — International Phone Number Handling

Since this system will be used globally, phone number normalization is critical.

In `sms/services.py`, the `normalize_phone()` function should:
- Accept numbers in any common format: `+233241234567`, `0241234567`, `00233241234567`, `233241234567`
- Strip all spaces, dashes, parentheses before processing
- **Not assume Ghana** — if a number starts with `+` it is already international, use as-is
- Store and display numbers in E.164 in `SMSLog`
- Each school deployment should configure its `DEFAULT_COUNTRY_CODE` in `.env` for local-format fallback

Add to `.env`:
```
DEFAULT_COUNTRY_CODE=233    # Ghana. Change per deployment country.
```

Optionally install `phonenumbers` library for robust parsing:
```
phonenumbers>=8.13.0
```

If `phonenumbers` is available, use `phonenumbers.parse()` with the country hint for validation.

---

## FILE STRUCTURE EXPECTED AFTER IMPLEMENTATION

```
sms/
├── __init__.py
├── apps.py
├── models.py          # SMSLog
├── services.py        # send_sms(), send_bulk_sms(), normalize_phone()
├── views.py           # BulkSMSView, SMSLogListView + recipient helpers
├── urls.py
├── admin.py
└── templates/
    └── sms/
        └── bulk_sms.html

fees/
├── signals.py         # post_save on FeePayment → auto SMS
└── apps.py            # registers signals in ready()
```

---

## IMPORTANT CONSTRAINTS

- SMS failures must **NEVER** raise exceptions that crash the main app flow
- Every SMS attempt (success, failure, or skip) must be logged to `SMSLog`
- Phone numbers stored and transmitted in E.164 (`+[country_code][number]`)
- API keys never hard-coded — always read from Django settings → `.env`
- `SMS_USE_SANDBOX=True` must print to logger only (no Twilio API call, no credits used)
- Message over 160 characters = 2 SMS credits; warn the user in the bulk SMS UI
- `DEFAULT_COUNTRY_CODE` in `.env` is the only Ghana-specific assumption; everything else is country-agnostic

---

## TWILIO API REFERENCE (for implementation)

```python
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

message = client.messages.create(
    body="Your message here",
    from_=settings.TWILIO_PHONE_NUMBER,
    to="+233241234567"
)

# message.sid  → unique message ID (e.g. "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
# message.status → "queued", "sent", "delivered", "failed", "undelivered"
```

**TwilioRestException codes to handle:**
- `21211` — Invalid 'To' phone number
- `21614` — 'To' number is not a valid mobile number
- `21408` — Permission to send to this region denied (trial accounts)
- `20003` — Authentication failure (wrong SID/token)

---

## PRE-IMPLEMENTATION CHECKLIST FOR THE AI CODING TOOL

Before writing any code, ask the user to confirm:

1. Read from the claude file if available and Infer from the project all the necessary architechure and modules that need to be understoond to be modified or ehanced to achieve this goal or scan the project to understand the project before making changes


---

*End of prompt. Implement tasks in order 1 → 8. Confirm model field names before writing signals or views.*

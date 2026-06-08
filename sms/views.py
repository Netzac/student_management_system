from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView

from student_core.models import Students

from .models import SMSLog
from .services import send_bulk_sms
from .utils import (
    build_all_guardian_recipients,
    build_class_recipients,
    build_individual_recipients,
    get_class_choices,
)


class BulkSMSPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.is_staff
            or request.user.has_perm("sms.can_send_bulk_sms")
        ):
            raise PermissionDenied("You do not have permission to send bulk SMS.")
        return super().dispatch(request, *args, **kwargs)


class BulkSMSView(BulkSMSPermissionMixin, LoginRequiredMixin, TemplateView):
    template_name = "sms/bulk_sms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["classes"] = get_class_choices()
        context["students"] = Students.objects.filter(
            status="1", delete_flag=0
        ).select_related("admin", "course_id").order_by(
            "admin__last_name", "admin__first_name"
        )
        context["recent_logs"] = SMSLog.objects.filter(trigger="bulk_sms")[:20]
        context["all_guardian_count"] = len(build_all_guardian_recipients())
        context["class_phone_counts"] = {
            str(cls.id): len(build_class_recipients(cls.id))
            for cls in context["classes"]
        }
        return context

    def post(self, request):
        group = request.POST.get("recipient_group")
        message = request.POST.get("message", "").strip()

        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect("bulk-sms")

        if group == "all_guardians":
            recipients = build_all_guardian_recipients()
        elif group == "by_class":
            class_id = request.POST.get("class_id")
            recipients = build_class_recipients(class_id)
        elif group == "individual":
            student_ids = request.POST.getlist("student_ids")
            recipients = build_individual_recipients(student_ids)
        else:
            messages.error(request, "Invalid recipient group.")
            return redirect("bulk-sms")

        if not recipients:
            messages.warning(request, "No recipients with phone numbers found.")
            return redirect("bulk-sms")

        result = send_bulk_sms(recipients, message, sent_by=request.user)
        messages.success(
            request,
            f"SMS sent: {result['sent']} delivered, "
            f"{result['failed']} failed, {result['skipped']} skipped.",
        )
        return redirect("bulk-sms")


class SMSLogListView(BulkSMSPermissionMixin, LoginRequiredMixin, ListView):
    model = SMSLog
    template_name = "sms/sms_logs.html"
    context_object_name = "logs"
    paginate_by = 50

from django.urls import path

from .views import BulkSMSView, SMSLogListView

urlpatterns = [
    path("bulk/", BulkSMSView.as_view(), name="bulk-sms"),
    path("logs/", SMSLogListView.as_view(), name="sms-logs"),
]

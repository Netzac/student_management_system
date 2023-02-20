
from django.urls import path
from django.views.generic import TemplateView 
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage


from .views import (
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceListView,
    InvoiceUpdateView,
    ReceiptCreateView,
    ReceiptUpdateView,
    FeeTypeCreateView, FeeTypeUpdateView, FeeTypeDeleteView, FeeTypeListView,ClassInvoiceCreateView,
    bulk_invoice,
    verify_online_payment,dashboard,BillsPaymentByRange,BillsPaymentByMonth,
)

urlpatterns = [
    path("list/", InvoiceListView.as_view(), name="invoice-list"),
    path("create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("create/class/", ClassInvoiceCreateView.as_view(), name="class-invoice-create"),
    path("<int:pk>/detail/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="invoice-update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    path("receipt/create", ReceiptCreateView.as_view(), name="receipt-create"),
    path("receipt/<int:pk>/update/", ReceiptUpdateView.as_view(), name="receipt-update"),
    path("bulk-invoice/", bulk_invoice, name="bulk-invoice"),

    path("dashboard/",dashboard, name="account-dashboard"),
    path("feetype/list/", FeeTypeListView.as_view(), name="feetype-list"),
    path("create", FeeTypeCreateView.as_view(), name="feetype-create"),
    path("feetype/<int:pk>/update/", FeeTypeUpdateView.as_view(), name="feetype-update"),
    path("feetype/<int:pk>/delete/", FeeTypeDeleteView.as_view(),name="feetype-delete"),

    path('report_by_date_range/', BillsPaymentByRange.as_view(),name='report-by-range'),
    path('report_by_month/', BillsPaymentByMonth.as_view(),name='report-by-month'),

    path("ajax/verify-online-payment/<ref>/<invoice>/<amount>/",verify_online_payment,name="verify-online-payment")
]
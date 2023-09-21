
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
    bulk_invoice, EarningsCreateView ,EarningsListView, EarningsUpdateView,EarningsDeleteView,DeductionsListView,DeductionsUpdateView,
    DeductionsDeleteView,  DeductionsCreateView,  RoleCreateView,RoleUpdateView,RoleListView,RoleDeleteView,
    verify_online_payment,dashboard,BillsPaymentByRange,BillsPaymentByMonth,
    save_taxtable,view_taxtable,delete_taxtable,taxtable,manage_taxtable,
    PayrollCreateView,PayrollListView,PayrollDeleteView,PayrollUpdateView,PayrollDetailView,
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

    ## Earnings 
    path("earnings/list/", EarningsListView.as_view(), name="earnings-list"),
    path("earnings/create/", EarningsCreateView.as_view(), name="earnings-create"),
    path("earnings/<int:pk>/update/", EarningsUpdateView.as_view(), name="earnings-update"),
    path("feetype/<int:pk>/delete/", EarningsDeleteView.as_view(),name="earnings-delete"),

    ## Deductions 
    path("deductions/list/", DeductionsListView.as_view(), name="deductions-list"),
    path("deductions/create/", DeductionsCreateView.as_view(), name="deductions-create"),
    path("deductions/<int:pk>/update/", DeductionsUpdateView.as_view(), name="deductions-update"),
    path("deductions/<int:pk>/delete/", DeductionsDeleteView.as_view(),name="deductions-delete"),

    ## Role 
    path("role/list/", RoleListView.as_view(), name="role-list"),
    path("role/create/", RoleCreateView.as_view(), name="role-create"),
    path("role/<int:pk>/update/", RoleUpdateView.as_view(), name="role-update"),
    path("role/<int:pk>/delete/", RoleDeleteView.as_view(),name="role-delete"),

    
    # Tax Table
    path('taxtable',taxtable,name='taxtable'),
    path('manage_taxtable',manage_taxtable,name='manage-taxtable'),
    path('manage_book/<int:pk>',manage_taxtable,name='manage-taxtable-pk'),
    path('view_taxtable/<int:pk>',view_taxtable,name='view-taxtable-pk'),
    path('save_taxtable',save_taxtable,name='save-taxtable'),
    path('delete_taxtable/<int:pk>',delete_taxtable,name='delete-taxtable'),

    # Payroll

    path("payroll/list/", PayrollListView.as_view(), name="payroll-list"),
    path("payroll/create/", PayrollCreateView.as_view(), name="payroll-create"),
    path("payroll/<int:pk>/detail/", PayrollDetailView.as_view(), name="payroll-detail"),
    path("payroll/<int:pk>/update/", PayrollUpdateView.as_view(), name="payroll-update"),
    path("payroll/<int:pk>/delete/", PayrollDeleteView.as_view(), name="payroll-delete"),


    path('report_by_date_range/', BillsPaymentByRange.as_view(),name='report-by-range'),
    path('report_by_month/', BillsPaymentByMonth.as_view(),name='report-by-month'),

    path("ajax/verify-online-payment/<ref>/<invoice>/<amount>/",verify_online_payment,name="verify-online-payment")
]
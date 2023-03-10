from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy,reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django.views.decorators.csrf import csrf_exempt
from requests import request

from student_core.models import AcademicTerm, Courses, SessionYearModel, Students as Student

from .forms import InvoiceItemFormset, InvoiceReceiptFormSet, Invoices,FeeTypeForm
from .models import Invoice, InvoiceItem, Receipt,FeeType

from .utils import get_prev_term_bills

class InvoiceListView(LoginRequiredMixin,ListView):
    template_name = 'student_account/invoice_list.html'

    def get_queryset(self):
        user =self.request.user
        user_type =user.user_type
        if user_type=='1':
            self.queryset = Invoice.objects.filter(session=self.request.current_session,term =self.request.current_term)
        elif user_type=='3':
            self.queryset = Invoice.objects.filter(session=self.request.current_session,term =self.request.current_term,student=user.students)
        return self.queryset
    
   

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = ['student','session','term']
    success_url = "/studentaccount/list"

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = InvoiceItemFormset(
                self.request.POST, prefix="invoiceitem_set"
            )
        else:
            context["items"] = InvoiceItemFormset(prefix="invoiceitem_set")
        return context

    def form_valid(self, form):
        id= self.request.POST.get('student')
        
        prev_term_bills = get_prev_term_bills(self.request.current_session_id)
        #print('previous',prev_term_bills)
        
        student=Student.objects.select_related("course_id").get(id=id)
        context = self.get_context_data()
        formset = context["items"]
        form.instance.class_for=student.course_id

        if prev_term_bills:
            try:
                form.instance.balance_from_previous_term= prev_term_bills.get(student=student).balance()
            except:
                form.instance.balance_from_previous_term= 0

        self.object = form.save()
        #print('object:', self.object)
        if self.object.id != None:
            if form.is_valid() and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return super().form_valid(form)

class ClassInvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = ['session','term','class_for']
    template_name='student_account/class_invoice_form.html'
    success_url = "/studentaccount/list"

    def get_context_data(self, **kwargs):
        context = super(ClassInvoiceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = InvoiceItemFormset(
                self.request.POST, prefix="invoiceitem_set"
            )
        else:
            context["items"] = InvoiceItemFormset(prefix="invoiceitem_set")
        return context

    def form_valid(self, form):
        cls_id=Courses.objects.get(id= self.request.POST.get('class_for'))
        session=SessionYearModel.objects.get(id=self.request.POST.get('session'))
        term=AcademicTerm.objects.get(id=self.request.POST.get('term'))
        students = Student.objects.filter(course_id=cls_id)
       
        prev_term_bills = get_prev_term_bills(self.request.current_session_id)

        #print('previous',prev_term_bills)
        bulk =[]
        prev_amount=0
        for student in students:
            #invoice =Invoice(student=student,session=session,term=term,class_for=cls_id)
            #bulk.append(Invoice(student=student,session=session,term=term,class_for=cls_id))
            #print("Class:", student.id,session,term,cls_id)
            if prev_term_bills:
                try:
                    prev_amount = prev_term_bills.get(student=student).balance()
                except:
                   prev_amount= 0
           
            saved = Invoice.objects.create(student=student,session=session,term=term,class_for=cls_id,balance_from_previous_term=prev_amount)
            form.instance.student=saved.student

           
            print("Saved",saved)
            context = self.get_context_data()
            formset = context["items"]
            self.object = saved
            if saved != None:
                if formset.is_valid():
                    formset.instance = self.object
                    formset.save()
           
        return redirect("invoice-list")

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    fields = "__all__"

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context["receipts"] = Receipt.objects.filter(invoice=self.object)
        context["items"] = InvoiceItem.objects.filter(invoice=self.object)
        return context


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    fields = ["student", "session", "term", "balance_from_previous_term"]

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["receipts"] = InvoiceReceiptFormSet(
                self.request.POST, instance=self.object
            )
            context["items"] = InvoiceItemFormset(
                self.request.POST, instance=self.object
            )
        else:
            context["receipts"] = InvoiceReceiptFormSet(instance=self.object)
            context["items"] = InvoiceItemFormset(instance=self.object)
        return context

    def form_valid(self, form):
      
        context = self.get_context_data()
        formset = context["receipts"]
        itemsformset = context["items"]
        if form.is_valid() and formset.is_valid() and itemsformset.is_valid():
            form.save()
            formset.save()
            itemsformset.save()
        return super().form_valid(form)


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    success_url = reverse_lazy("invoice-list")


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment"]
    success_url = reverse_lazy("invoice-list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        invoice = Invoice.objects.get(pk=self.request.GET["invoice"])
        obj.invoice = invoice
        obj.save()
        return redirect("invoice-list")

    def get_context_data(self, **kwargs):
        context = super(ReceiptCreateView, self).get_context_data(**kwargs)
        invoice = Invoice.objects.get(pk=self.request.GET["invoice"])
        context["invoice"] = invoice
        return context


class ReceiptUpdateView(LoginRequiredMixin, UpdateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment"]
    success_url = reverse_lazy("invoice-list")


class ReceiptDeleteView(LoginRequiredMixin, DeleteView):
    model = Receipt
    success_url = reverse_lazy("invoice-list")






class FeeTypeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = FeeType
    form_class = FeeTypeForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("feetype-list")
    success_message = "New Fee type successfully added"


class FeeTypeListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = FeeType
    template_name = "feetype_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = FeeTypeForm()
        return context

class FeeTypeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = FeeType
    fields = ["type"]
    success_url = reverse_lazy("feetype-list")
    success_message = "FeeType successfully updated."
    template_name = "hod_template/mgt_form.html"


class FeeTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = FeeType
    success_url = reverse_lazy("feetype-list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.type)
        messages.success(self.request, self.success_message.format(obj.type))
        return super(FeeTypeDeleteView, self).delete(request, *args, **kwargs)


@login_required
def bulk_invoice(request):
    return render(request, "account/bulk_invoice.html")


from paystackapi.transaction import Transaction

@csrf_exempt
def verify_online_payment(request,ref,invoice,amount):

    
    redirect_url = reverse('receipt-create')
    response = Transaction.verify(reference=str(ref))
    print("response: ",response,ref)

   
    invoice = Invoice.objects.get(pk=invoice)
    obj = Receipt(invoice=invoice,amount_paid=amount)
    obj.save()
    messages.success(request,"Thank You! Payment made successfully.")
    return redirect("invoice-list")


from django.db.models import Sum,Count
# from functools import reduce
# from queryset_sequence import QuerySetSequence

def dashboard(request):

    rs = Student.objects.all()
    rs_count =rs.count()
    rs_invoices_unfiltered = Invoice.objects.all().order_by('class_for')
    rs_invoices = rs_invoices_unfiltered.values_list('id' ,flat =True)
    rs_receipts = Receipt.objects.filter(invoice__in = rs_invoices)
    rs_receipts_count = rs_receipts.distinct('invoice__student').count()
    rs_inv_item_amt = InvoiceItem.objects.aggregate(Sum('amount'))['amount__sum']
    rs_recipts_amt = Receipt.objects.aggregate(Sum('amount_paid'))['amount_paid__sum']
    
    rs_arrears = {}
    rs_fully_paid ={}
    cls_labels = Courses.objects.all().values_list('course_name', flat=True)
    key = 0
    for inv in rs_invoices_unfiltered:
        key = str(inv.class_for.id)
        bal =inv.balance()
        if bal!=0:
            rs_arrears.update({key:rs_arrears.get(key,0)+1})
            #cls_labels.add(inv.class_for.course_name)
        elif bal==0:
            rs_fully_paid.update({key:rs_arrears.get(key,0)+1})
            #cls_labels.add(inv.class_for.course_name)


   
      
       
    arrears_list =list(rs_arrears.values())
    cls_list  = list(cls_labels)

    print('Arrears: ',arrears_list,cls_list )
    #rs_invoices_class = rs_invoices_unfiltered.values('student__course_id').annotate(cls_inv=Count('invoice_invoice_set.all()'))

    context={"total_students":rs_count,
             "paying_students" :rs_receipts_count,
              "none_paying_students":rs_count-rs_receipts_count,
              "total_arrears": rs_inv_item_amt-rs_recipts_amt,
              "total_paid": rs_recipts_amt,
              "cls_labels": cls_list,
              "arrears":arrears_list,
              "fully_paid":list(rs_fully_paid)}
    return render(request,'student_account/dashboard.html',context)


    '''Slick Reportingg starts here'''
from slick_reporting.views import SlickReportView
from slick_reporting.fields import SlickReportField   
from django.utils.translation import gettext_lazy as _ 

class BillsPaymentByRange(SlickReportView):
    # The model where you have the data
    report_model = Receipt
    template_name ='student_account/rpt_by_date.html'
    
    # the main date field used for the model.
    date_field = 'date_paid' # or 'order__date_placed'
    # this support traversing, like so
    # date_field = 'order__date_placed'
     # The columns you want to display
    group_by = 'date_paid'

    columns = ['date_paid',SlickReportField.create(method=Sum, field='amount_paid', name='amount_paid__sum', verbose_name=_('Total Paid '))]
               # a Slick Report Field is responsible for carrying on the needed calculation(s).]
     # Charts
    chart_settings = [
     {
        'type': 'bar',
        'engine_name': 'chartsjs',
        'data_source': ['amount_paid__sum'],
        'title_source': ['date_paid'],
        'title':'Cbart Of Payments By Date',
        'plot_total': True
     },
    ]
    def format_row(self, row_obj):
        """ A hook to format each row . This method gets called on each row in the results.
        :param row_obj: a dict representing a single row in the results
            :return: A dict representing a single row in the results
            """
        row_obj['date_paid'] = row_obj['date_paid'].strftime('%d %b %Y')#date(row_obj['date_paid'], 'd-m-y H:i')

        return row_obj

  

    # A foreign key to group calculation on
class BillsPaymentByMonth(SlickReportView):
    
    report_model = Receipt
    template_name ='student_account/rpt_by_month.html'
    date_field = 'date_paid'
    group_by = 'invoice__created_at'
    columns = ['invoice__created_at',
               '__time_series__',
               # __time_series__ is special column name used to control the placing of the time series columns inside your columns.
               # Default would be appended to the end of the columns.
               SlickReportField.create(Sum, 'amount_paid', name='paid__sum', verbose_name=_('Grand Sum')),
               ]

    time_series_pattern = 'monthly'
    time_series_columns = [
        SlickReportField.create(Sum, 'amount_paid', name='paid__sum', verbose_name=_('Sum of'))
    ]

    def format_row(self, row_obj):
        """ A hook to format each row . This method gets called on each row in the results.
        :param row_obj: a dict representing a single row in the results
            :return: A dict representing a single row in the results
            """
        row_obj['invoice__created_at'] = row_obj['invoice__created_at'].strftime('%d %b %Y')#date(row_obj['date_paid'], 'd-m-y H:i')

        return row_obj

  
    chart_settings = [
        {'type': 'bar',
         'engine_name': 'chartsjs',
         'data_source': ['paid__sum'],
         'title_source': ['date_paid'],
         'title': 'Total Payments per Month',
         'plot_total': True  # Plot Totals !
         }
    ]

   
from datetime import date
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy,reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from requests import request

from student_core.models import AcademicTerm, Courses, SessionYearModel, Students as Student, Staffs as Staff, \
    Bank,Role
from school.models import School
from .forms import (
    InvoiceItemFormset, InvoiceReceiptFormSet, Invoices,FeeTypeForm, BankForm,DeductionsForm, 
    RoleForm, EarningsForm, TaxTableForm,DeductionsItemFormset,EarningsItemFormset,)
from .models import ( Invoice, InvoiceItem, Receipt,FeeType, Earnings, 
                     Deductions,TaxTable, Payroll,Staff_Deductions,Staff_Earnings,)

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
    
# Staff Earnings setup
class EarningsCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Earnings
    form_class = EarningsForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("earnings-list")
    success_message = "Earnings Type successfully added"

class EarningsListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Earnings
    template_name = "earnings_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = EarningsForm()
        return context

class EarningsUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Earnings
    fields = ["type"]
    success_url = reverse_lazy("earnings-list")
    success_message = "Earnings successfully updated."
    template_name = "hod_template/mgt_form.html"


class EarningsDeleteView(LoginRequiredMixin, DeleteView):
    model = Earnings
    success_url = reverse_lazy("earnings-list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.type)
        messages.success(self.request, self.success_message.format(obj.type))
        return super(FeeTypeDeleteView, self).delete(request, *args, **kwargs)

# Staff Deductions setup
class DeductionsCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Deductions
    form_class = DeductionsForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("deductions-list")
    success_message = "Deductions type successfully added"

class DeductionsListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Deductions
    template_name = "deductions_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = DeductionsForm()
        return context

class DeductionsUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Deductions
    fields = ["type"]
    success_url = reverse_lazy("deductions-list")
    success_message = "Deductions successfully updated."
    template_name = "hod_template/mgt_form.html"


class DeductionsDeleteView(LoginRequiredMixin, DeleteView):
    model = Deductions
    success_url = reverse_lazy("deductions-list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.type)
        messages.success(self.request, self.success_message.format(obj.type))
        return super(DeductionsDeleteView, self).delete(request, *args, **kwargs)

# Banks setup
class BankCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Bank
    form_class = BankForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("bank-list")
    success_message = "Bank successfully added"

class BankListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Bank
    template_name = "student_account/bank_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = BankForm()
        return context

class BankUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Bank
    fields = ["name"]
    success_url = reverse_lazy("bank-list")
    success_message = "Bank successfully updated."
    template_name = "hod_template/mgt_form.html"


class BankDeleteView(LoginRequiredMixin, DeleteView):
    model = Bank
    success_url = reverse_lazy("bank-list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.type)
        messages.success(self.request, self.success_message.format(obj.type))
        return super(DeductionsDeleteView, self).delete(request, *args, **kwargs)


# Staff Role setup
class RoleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("role-list")
    success_message = "Role type successfully added"

class RoleListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Role
    template_name = "student_account/role_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RoleForm()
        return context

class RoleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Role
    fields = ["type"]
    success_url = reverse_lazy("role-list")
    success_message = "Role successfully updated."
    template_name = "hod_template/mgt_form.html"


class RoleDeleteView(LoginRequiredMixin, DeleteView):
    model = Role
    success_url = reverse_lazy("Role-list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.type)
        messages.success(self.request, self.success_message.format(obj.type))
        return super(RoleDeleteView, self).delete(request, *args, **kwargs)


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

    rs_receipts_count=rs_receipts.values_list('invoice__student',flat=True).distinct().count()
    #rs_receipts_count = rs_receipts.distinct('invoice__student').count()


    rs_inv_item_amt = InvoiceItem.objects.aggregate(Sum('amount'))['amount__sum']
    rs_recipts_amt = Receipt.objects.aggregate(Sum('amount_paid'))['amount_paid__sum']

    rs_inv_item_amt = rs_inv_item_amt if rs_inv_item_amt else 0
    rs_recipts_amt = rs_recipts_amt if rs_recipts_amt else 0
    
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

   

   #Views for Payroll and Staff Accounts



# TaxTable   
'''|Extra views for the taxtable'''
def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host' : abs_uri,
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'jSchoolAnywhere',
    }

    return context
@login_required
def taxtable(request):
    context = context_data(request)
    context['page'] = 'taxtable'
    context['page_title'] = "Tax Table List"
    context['taxtable'] = TaxTable.objects.all().order_by('id')
    return render(request, 'student_account/taxtable.html', context)

@login_required
def save_taxtable(request):
    resp = { 'status': 'failed', 'msg' : '' }
    #print(request)
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            gradebook = TaxTable.objects.get(id = post['id'])
            form = TaxTableForm(request.POST, instance=gradebook)
        else:
            form = TaxTableForm(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Tax Table successfully saved .")
            else:
                messages.success(request, "Tax Table updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "No data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_taxtable(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_taxtable'
    context['page_title'] = 'View Tax Table'
    if pk is None:
        context['taxtable'] = {}
    else:
        context['taxtable'] = TaxTable.objects.get(id=pk)
    
    return render(request, 'student_account/view_taxtable.html', context)

@login_required
def manage_taxtable(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_taxtable'
    context['page_title'] = 'Manage Tax Table'
   
    if pk is None:
        context['taxtable'] = {}
    else:
        context['taxtable'] = TaxTable.objects.get(id=pk)
    print('context:',context)
    return render(request, 'student_account/manage_taxtable.html', context)

@login_required
def delete_taxtable(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'ID is invalid'
    else:
        try:
            TaxTable.objects.filter(pk = pk).delete()
            messages.success(request, "Tax table item deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


class PayrollListView(LoginRequiredMixin,ListView):
    template_name = 'student_account/payroll_list.html'

    def get_queryset(self):
        user =self.request.user
        user_type =user.user_type
        if user_type=='1':
            self.queryset = Payroll.objects.all().distinct()
        elif user_type=='2':
            self.queryset = Payroll.objects.filter(staff=user.staffs).distinct()
        return self.queryset
    

class PayrollCreateView(LoginRequiredMixin, CreateView):
    model = Payroll
    fields = ['staff','basic_pay','period']
    success_url = "/studentaccount/payroll/list"

    def get_context_data(self, **kwargs):
        context = super(PayrollCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["d_items"] = DeductionsItemFormset(
                self.request.POST, prefix="deductionsItem_set"
            )
            context["e_items"] = EarningsItemFormset(
                self.request.POST, prefix="earningsItem_set"
            )
        else:
            context["d_items"] = DeductionsItemFormset(prefix="deductionsItem_set")
            context["e_items"] = EarningsItemFormset(prefix="earningsItem_set")
        return context

    def form_valid(self, form):
        id= self.request.POST.get('staff')
        
        staff=Staff.objects.get(id=id)
        context = self.get_context_data()
        formset_d =  context["d_items"] # DeductionsItemFormset(self.request.POST or None, prefix="DeductionsItem_set")
        formset_e = context["e_items"] #EarningsItemFormset(self.request.POST or None,prefix="EarningsItem_set")
        #form.instance.class_for=student.course_id

        #print("Post",self.request.POST,staff)
        saved = form.save()
        
        #print('formsets:', saved )

        if saved.id != None:
            if formset_d.is_valid() :
                print('formset_d is valid:', staff.id)
                object_d = formset_d.save(commit=False)
               
                #object_d.instance = saved
                for d in object_d:
                    d.staff = saved.staff
                    d.period = saved.period
                    d.payroll = saved
                    d.save()
            if formset_e.is_valid() :
                print('formset_e is valid:', staff.id)
                object_e = formset_e.save(commit=False)
                for e in object_e:
                    e.staff = saved.staff
                    e.period=saved.period
                    e.payroll = saved
                    e.save()
               
            else:
                print("formset_d valid =", formset_d.is_valid())
        return super().form_valid(form)
    
from num2words import num2words  
class PayrollDetailView(LoginRequiredMixin, DetailView):
        model = Payroll
        fields = "__all__"

        def get_context_data(self, **kwargs):
            context = super(PayrollDetailView, self).get_context_data(**kwargs)
            payroll_obj = Payroll.objects.filter(staff=self.object.staff)[0]
            context["payroll"] = payroll_obj
            context["net_pay_in_words"] = num2words(payroll_obj.net_pay)
            context["deductions"] = Staff_Deductions.objects.filter(staff=self.object.staff)
            context["earnings"] = Staff_Earnings.objects.filter(staff=self.object.staff)
            context["adminSign"] = School.objects.first().adminSignature
            return context


class PayrollUpdateView(LoginRequiredMixin, UpdateView):
    model = Payroll
    fields = ['staff','net_pay']

    def get_context_data(self, **kwargs):

        context = super(PayrollUpdateView, self).get_context_data(**kwargs)
        q_deductions = Staff_Deductions.objects.filter(staff=self.object.staff)
        q_earnings = Staff_Earnings.objects.filter(staff=self.object.staff)
        if self.request.POST:
            context["d_items"] = DeductionsItemFormset(
                self.request.POST, prefix="deductionsItem_set",queryset=q_deductions
            )
            context["e_items"] = EarningsItemFormset(
                self.request.POST, prefix="earningsItem_set",queryset=q_earnings
            )
        else:
            #print("Staff is:", q_deductions[0].pk)
            context["d_items"] = DeductionsItemFormset(prefix="deductionsItem_set",instance=self.object.staff)
            context["e_items"] = EarningsItemFormset(prefix="earningsItem_set",instance=self.object.staff)
        return context

    def form_valid(self, form):
      
        context = self.get_context_data()
        formset_d = context["d_items"]
        formset_e = context["e_items"]
        
        saved = form.save()
        if saved.id != None:

            if formset_d.is_valid():
                d_instance = formset_d.save(commit=False)
               
                for obj in formset_d.deleted_objects:
                    obj.delete()
                for d in d_instance:
                    d.staff = saved.staff
                    d.save()
            if formset_e.is_valid():               
                e_instance = formset_e.save(commit=False)
                for obj in formset_e.deleted_objects:
                    obj.delete()
                for e in e_instance:
                    e.staff = saved.staff
                    e.save()
        return super().form_valid(form)


class PayrollDeleteView(LoginRequiredMixin, DeleteView):
     
    model = Payroll
    success_url = reverse_lazy("payroll-list")
    template_name = "student_account/payroll_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print("Deletion reach here",obj.type)
       # Staff_Deductions.objects.filter(staff=obj.staff).delete()
       # Staff_Earnings.objects.filter(staff=obj.staff).delete()
        messages.success(self.request, self.success_message.format(obj.staff))
        return super(PayrollDeleteView, self).delete(request, *args, **kwargs)
    
from django.db import transaction
import datetime
from datetime import datetime
def payroll_finalize():

   # month = date.month()
   # yr = date.year()
    period =  datetime.now().strftime('%m-%Y')
    curr_payroll = Payroll.objects.filter(period=period)
    print("current payroll",curr_payroll,period)
    #with transaction.atomic():
    update_list =[]
    for r in curr_payroll:
        r.deductions = r.calcDeductions()
        r.earnings = r.calcEarnings()
        r.net_pay =r.calcNetPay()
        r.Paid_Date = date.today()
        update_list.append(r)

    Payroll.objects.bulk_update(update_list,['deductions','earnings','net_pay','paid_date'])
    return None

class PayrollFinalize(ListView):

    model=Payroll
    template_name="student_account/bank_advice_slip.html"

    
    def get_queryset(self):

        payroll_finalize()
           # yr = date.year()
        period =datetime.now().strftime('%m-%Y')

        
        user_type = self.request.user.user_type
        if user_type=='1':
            return Payroll.objects.select_related('staff').filter(period=period)
        # elif user_type=='2':
        #     return RequiredItem.objects.filter(cls=get_teacher_cls_id(self.request))
        # elif user_type=='3':
        #     return RequiredItem.objects.filter(cls=self.request.user.students.course_id)

    def get_context_data(self, **kwargs):
        try:
            school = School.objects.all().first()
        except:
            school={}
        period =datetime.now().strftime('%B-%Y')
        context = super().get_context_data(**kwargs)
        context["payroll_period"] = period
        context["bank"] = school.bank
        context["school"] = school
        return context
    

class PayrollPaye(ListView):

    model=Payroll
    template_name="student_account/payroll_paye.html"

    
    def get_queryset(self):

        payroll_finalize()
           # yr = date.year()
        period =datetime.now().strftime('%m-%Y')

        
        user_type = self.request.user.user_type
        if user_type=='1':
            return Payroll.objects.select_related('staff').filter(period=period)
        # elif user_type=='2':
        #     return RequiredItem.objects.filter(cls=get_teacher_cls_id(self.request))
        # elif user_type=='3':
        #     return RequiredItem.objects.filter(cls=self.request.user.students.course_id)

    def get_context_data(self, **kwargs):
        try:
            school = School.objects.all().first()
        except:
            school={}
        period =datetime.now().strftime('%B-%Y')
        context = super().get_context_data(**kwargs)
        context["payroll_period"] = period
        context["bank"] = school.bank
        context["school"] = school
        return context
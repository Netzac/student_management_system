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


class InvoiceListView(LoginRequiredMixin,ListView):
    model = Invoice
    template_name = 'student_account/invoice_list.html'

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
        print('Student:',id)
        student=Student.objects.select_related("course_id").get(id=id)
        context = self.get_context_data()
        formset = context["items"]
        form.instance.class_for=student.course_id
        self.object = form.save()
        print('object:', self.object)
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
        term=AcademicTerm.objects.get(id=self.request.POST.get('session'))
        students = Student.objects.filter(course_id=cls_id)
        bulk =[]
        for student in students:
            #invoice =Invoice(student=student,session=session,term=term,class_for=cls_id)
            #bulk.append(Invoice(student=student,session=session,term=term,class_for=cls_id))
            print("Class:", student.id,session,term,cls_id)
        
            saved = Invoice.objects.create(student=student,session=session,term=term,class_for=cls_id)
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
def verify_online_payment(request,ref,invoice):
    redirect_url = reverse('receipt-create')
    response = Transaction.verify(reference=str(ref))
    print("response: ",response,ref)

   
    invoice = Invoice.objects.get(pk=invoice)
    obj = Receipt(invoice=invoice,amount_paid=10)
    obj.save()
    messages.success(request,"Thank You! Payment made successfully.")
    return redirect("invoice-list")
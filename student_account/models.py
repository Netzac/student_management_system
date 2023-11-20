from cProfile import label
from enum import unique
from tabnanny import verbose
from unittest.util import _MAX_LENGTH
from django.db import models
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from student_core.models import SessionYearModel, AcademicTerm, Courses as StudentClass
from student_core.models import Students, Staffs



class Earnings(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(unique=True,max_length=150)
    description = models.CharField(max_length=200,blank=True)

    objects= models.Manager()

    def __str__(self):
        return self.type

class Deductions(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(unique=True,max_length=150)
    description = models.CharField(max_length=200,blank=True)

    objects= models.Manager()

    def __str__(self):
        return self.type


class FeeType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(unique=True,max_length=150)
    description = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return self.type

#Staff Roles
class Role(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(unique=True,max_length=150)
    description = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return self.type




        
class Invoice(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True, verbose_name='Invoice Date')
    session = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    class_for = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    balance_from_previous_term = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("closed", "Closed")],
        default="active",
    )
    objects= models.Manager()
   
    class Meta:
        ordering = ["student", "term"]
    def __str__(self):
        return f"{self.id}________________{self.student}________________{self.created_at.strftime('%d %b %Y')} '                       '"
    
    def get_owner(self):
        return f"{self.student}"

    def balance(self):
        payable = self.total_amount_payable()
        paid = self.total_amount_paid()
        return payable - paid

    def amount_payable(self):
        items = InvoiceItem.objects.filter(invoice=self)
        total = 0
        for item in items:
            total += item.amount
        return total

    def total_amount_payable(self):
        return self.balance_from_previous_term + self.amount_payable()

    def total_amount_paid(self):
        receipts = Receipt.objects.filter(invoice=self)
        amount = 0
        for receipt in receipts:
            amount += receipt.amount_paid
        return amount

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"pk": self.pk})


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    feetype= models.ForeignKey(FeeType,on_delete=models.DO_NOTHING)
    amount = models.IntegerField()

    objects = models.Manager()

class Receipt(models.Model):
    invoice = models.ForeignKey(Invoice, verbose_name="Bills" ,on_delete=models.CASCADE)
    amount_paid = models.IntegerField(verbose_name="Amount")
    date_paid = models.DateField(default=timezone.now,verbose_name="Payment Date")
    comment = models.CharField(max_length=200, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"Receipt on {self.date_paid}"


# Models for Accounts and Payroll

class TaxTable(models.Model):
    id = models.AutoField(primary_key=True)
    chargeableIncome = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    date_added=models.DateTimeField(auto_now=True)

    class meta:
        ordering=['id']
    def __str__(self):
        return f"{self.chargeableIncome} @ {self.rate}" 
    

    # Staff Payroll

class Payroll(models.Model):
    id=  models.AutoField(primary_key=True)
    deductions = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    earnings =  models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    payable_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    basic_pay = models.DecimalField(verbose_name="Basic Salary",max_digits=18, decimal_places=2, default=0.00)
    net_pay = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    staff = models.ForeignKey(Staffs, on_delete=models.DO_NOTHING)
    period  = models.CharField(max_length=50)
    paid_date = models.DateField(auto_now_add=True, verbose_name='Paid Date')

    objects= models.Manager()

    def calcDeductions(self):
        items = Staff_Deductions.objects.filter(staff=self.staff)
        total = 0
        for item in items:
            total += item.amt
        return total
    
    def cakcEarnings(self):
        items = Staff_Earnings.objects.filter(staff=self.staff)
        total = 0
        for item in items:
            total += item.amt
        return total
    
    def calcPayableTax(self):
        items = TaxTable.objects.all()
        income =self.basic_pay
        tax = 0

        for item in items:
            if income >= item.chargeableIncome:
                tax += round((item.chargeableIncome * item.rate * Decimal(0.01)),2)
                income -= item.chargeableIncome
        return tax
    
    def calcNetPay(self):
        net = 0
        staffEarnings = Decimal (self.cakcEarnings())
        staffDeductions = Decimal(self.calcDeductions())
        tax = self.calcPayableTax()
        grossPay = self.basic_pay  + staffEarnings
        net = grossPay - staffDeductions - tax

        return net




    class Meta:
        ordering = ["staff"]

    def __str__(self):
       return f"{self.staff}"
        
    def get_absolute_url(self):
        return reverse("payroll-detail", kwargs={"pk": self.pk})

class Staff_Deductions(models.Model):
    id=  models.AutoField(primary_key=True)
    deductions =  models.ForeignKey(Deductions, on_delete=models.DO_NOTHING)
    staff = models.ForeignKey(Staffs, on_delete=models.DO_NOTHING)
    amt = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    period  = models.CharField(max_length=50)
    payroll = models.ForeignKey(Payroll,on_delete=models.CASCADE)

    objects= models.Manager()

    class Meta:
        ordering = ["staff"]

    # def __str__(self):
    #     f"{self.staff}"
    # def get_absolute_url(self):
    #     return reverse("invoice-detail", kwargs={"pk": self.pk})
    
class Staff_Earnings(models.Model):
    id=  models.AutoField(primary_key=True)
    earnings =  models.ForeignKey(Earnings, on_delete=models.DO_NOTHING)
    staff = models.ForeignKey(Staffs, on_delete=models.DO_NOTHING)
    amt =  models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    period  = models.CharField(max_length=50)
    payroll = models.ForeignKey(Payroll,on_delete=models.CASCADE)

    objects= models.Manager()

    class Meta:
        ordering = ["staff"]

    # def __str__(self):
    #     f"{self.staff}"
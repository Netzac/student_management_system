from cProfile import label
from enum import unique
from tabnanny import verbose
from unittest.util import _MAX_LENGTH
from django.db import models
from django.urls import reverse
from django.utils import timezone

from student_core.models import SessionYearModel, AcademicTerm, Courses as StudentClass
from student_core.models import Students



class Earnings(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(unique=True,max_length=150)
    description = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return self.type

class Deductions(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(unique=True,max_length=150)
    description = models.CharField(max_length=200,blank=True)

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



from django.forms import (
    Form,ModelForm,inlineformset_factory, 
    modelformset_factory
)

from django import forms
from .models import FeeType, Invoice, InvoiceItem, Receipt, Deductions,Earnings, Role,TaxTable

InvoiceItemFormset = inlineformset_factory(
    Invoice, InvoiceItem, fields=["feetype", "amount"], extra=1, can_delete=True
)

InvoiceReceiptFormSet = inlineformset_factory(
    Invoice,
    Receipt,
    fields=("amount_paid", "date_paid", "comment"),
    extra=0,
    can_delete=True,
)

Invoices = modelformset_factory(Invoice, exclude=(), extra=4)

class EarningsForm(ModelForm):
    prefix = "Earnings"

    class Meta:
        model = Earnings
        fields = ["type"]

class DeductionsForm(ModelForm):
    prefix = "Deductions"

    class Meta:
        model = Deductions
        fields = ["type"]

class FeeTypeForm(ModelForm):
    prefix = "Fee Type"

    class Meta:
        model = FeeType
        fields = ["type"]

class RoleForm(ModelForm):
    prefix = "Role"

    class Meta:
        model = Role
        fields = ["type"]


# TaxTable Form
class TaxTableForm(forms.ModelForm):
   
    chargeableIncome = forms.DecimalField()
    rate= forms.DecimalField(max_value=100,min_value=0,decimal_places=2)


    class Meta:
        fields=['id','chargeableIncome','rate']
        model = TaxTable

    def clean_grade(self):
        id = int(self.data['id']) if (self.data['id']).isnumeric() else 0
        rate = self.changed_data['rate'] if (self.data['rate']).isnumeric() else 0.0
        chargeableIncome = self.cleaned_data['chargeableIncome']  if (self.data['chargeableIncome']).isnumeric() else 0.0
        try:
            if id > 0:
                taxtable = TaxTable.objects.exclude(id = id).get(chargeableIncome = chargeableIncome)
            else:
                taxtable = TaxTable.objects.get(chargeableIncome = chargeableIncome)
        except:
            return rate
        raise forms.ValidationError("Id already exists on the Database.")
  
from django.forms import (
    Form,ModelForm,inlineformset_factory, 
    modelformset_factory
)


from .models import FeeType, Invoice, InvoiceItem, Receipt, Deductions,Earnings, Role

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
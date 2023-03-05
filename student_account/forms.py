from django.forms import (
    Form,ModelForm,inlineformset_factory, 
    modelformset_factory
)


from .models import FeeType, Invoice, InvoiceItem, Receipt

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


class FeeTypeForm(ModelForm):
    prefix = "Fee Type"

    class Meta:
        model = FeeType
        fields = ["type"]
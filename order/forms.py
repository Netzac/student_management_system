from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
	DIVISION_CHOICES = (
		('Accra City', 'Accra City'),
		('Kumasi City', 'Kumasi City'),
		
	)

	DISCRICT_CHOICES = (
		('District1', 'District.1'), 
		('District.2', 'District.2'),
		('District.3', 'District.3'),
		('District.4', 'District.4'),
		('District.5', 'District.5'),
	)

	PAYMENT_METHOD_CHOICES = (
		('Paypal', 'Paypal'),
		('Credit Card','Credit Card'),
        ('Mobile Money','Mobile Money')
	)

	division = forms.ChoiceField(choices=DIVISION_CHOICES)
	district =  forms.ChoiceField(choices=DISCRICT_CHOICES)
	payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect())

	class Meta:
		model = Order
		fields = ['name', 'email', 'phone', 'address', 'division', 'district', 'zip_code', 'payment_method', 'account_no', 'transaction_id']
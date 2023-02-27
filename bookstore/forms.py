from django import forms
from crispy_forms.helper import FormHelper
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, modelformset_factory
from .models import RequiredItem, Review, Stationery


class ReviewForm(forms.ModelForm):
    review_star = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    review_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write Your Review'}))

    class Meta:
        model = Review
        fields = [
            'review_star',
            'review_text'
        ]
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    
class StationeryForm(ModelForm):
    prefix = "Stationery"

    class Meta:
        model = Stationery
        fields = ["item",'desc']


RequiredItemFormset = modelformset_factory(
    RequiredItem,fields=('item','qty','cls'),can_delete=True,extra=1
)

EditRequiredItemFormset = modelformset_factory(
    RequiredItem,fields=('item','qty','cls'),can_delete=True,extra=0
)
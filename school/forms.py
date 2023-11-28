from django import forms
from school.models import School

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        exclude = ['student_id']
        widgets = {
            'name'  :   forms.TextInput(attrs={'class':'form-control','Placeholder':'School Name'}),
            'phone'  :   forms.TextInput(attrs={'class':'form-control','Placeholder':'Motto'}),
            'phone'  :   forms.TextInput(attrs={'class':'form-control','Placeholder':'Phone Number'}),
            'email'  :   forms.EmailInput(attrs={'class':'form-control','Placeholder':'Email Address'}),
            'address'  :   forms.TextInput(attrs={'class':'form-control','Placeholder':'Address'}),
            'branch'  :   forms.TextInput(attrs={'class':'form-control','Placeholder':'Branch'}),
            'bank'  :   forms.Select(attrs={'class':'form-control','Placeholder':'Bank'}),
            'admin'  :   forms.Select(attrs={'class':'form-control','Placeholder':'Administrator'}),
            'adminSignature'  :   forms.FileInput(attrs={'class':'form-control'}),
            'logo'  :   forms.FileInput(attrs={'class':'form-control','Placeholder':'Logo'}),
            'seal'  :   forms.FileInput(attrs={'class':'form-control','Placeholder':'Seal or Stamp'}),
        }

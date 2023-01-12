from django import forms
from school.models import School

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        exclude = ['student_id']
        widgets = {
            'name'  :   forms.TextInput(attrs={'class':'form-control'}),
            'phone'  :   forms.TextInput(attrs={'class':'form-control'}),
            'email'  :   forms.EmailInput(attrs={'class':'form-control'}),
            'address'  :   forms.TextInput(attrs={'class':'form-control'}),
            'branch'  :   forms.TextInput(attrs={'class':'form-control'}),
            'admin'  :   forms.Select(attrs={'class':'form-control'}),
            'adminSignature'  :   forms.FileInput(attrs={'class':'form-control'}),
            'logo'  :   forms.FileInput(attrs={'class':'form-control'}),
            'seal'  :   forms.FileInput(attrs={'class':'form-control'}),
        }

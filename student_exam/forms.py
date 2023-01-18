from email.policy import default
from pyexpat import model
from typing_extensions import Required
# from tkinter import Widget
from django.forms.widgets import NumberInput  
from unicodedata import name
from django.forms import ModelForm, Textarea
#from django.contrib.auth.models import User
from django import forms


from . import models
from  student_core.models  import CustomUser as User, Courses, Subjects



class AssignmentForm(ModelForm):
    upload = forms.FileField(
        required=False,
        label='Select a file',
        help_text='max. 42 megabytes'
    )
    due_date = forms.DateField(
       widget = NumberInput(attrs={'type':'date'}))  
    # subject = forms.ModelChoiceField(label="Subject" ,queryset=Subjects.objects.all(),)
    # course = forms.ModelChoiceField(label="Class" ,queryset=Courses.objects.all(),)
    # # course = forms.ChoiceField(label="Class", choices=course_list, widget=forms.Select(attrs={"class":"form-control"}))
    # content = forms.Textarea()
    

    class Meta:
        model = models.Assignment
        fields = ['title','content','upload','due_date','course','subject']


class SubmissionForm(ModelForm):
    answer = forms.CharField(
        required=True,
        widget=Textarea())
    upload = forms.FileField(required=False)

    class Meta:
        model = models.Submission
        fields = ['answer','upload']



class PassForm(forms.Form):
    passcode = forms.CharField()

    class Meta:
        fields = "passcode"


class AssignmentSearchForm(forms.Form):
    q = forms.CharField()

    class Meta:
        fields = "q"
        errorlist = {
            'q': '',
        }


class SubmissionSearchForm(forms.Form):
    q = forms.CharField()

    class Meta:
        fields = "q"


class GradeForm(forms.Form):
    grade = forms.CharField()
    feedback = forms.CharField();

    class Meta:
        fields = ['grade','feedback']


class FeedbackForm(forms.Form):
    feedback = forms.TimeField()
    
    class Meta:
        fields = ['feedback']

class GradeBookForm(forms.ModelForm):
    lb = forms.IntegerField(required=True,help_text='For 70-100 enter 70 ')
    grade = forms.CharField(required=True,help_text='1 or A ')
    remark= forms.TextInput()

    class Meta:
        fields=['lb','grade','remark']
        model = models.Gradebook

class SaveGradebook(forms.ModelForm):
   
    lb = forms.IntegerField(required=True,help_text='For 70-100 enter 70 ')
    grade = forms.CharField(required=True,help_text='1 or A ')
    remark= forms.TextInput()


    class Meta:
        fields=['lb','grade','remark']
        model = models.Gradebook

    def clean_grade(self):
        id = int(self.data['id']) if (self.data['id']).isnumeric() else 0
        grade = self.cleaned_data['grade']
        try:
            if id > 0:
                gradebook = models.Gradebook.objects.exclude(id = id).get(grade = grade)
            else:
                gradebook = models.Gradebook.objects.get(grade = grade)
        except:
            return grade
        raise forms.ValidationError("Id already exists on the Database.")
  


'''Overall Gradebook Forms'''

class OverallGradeBookForm(forms.ModelForm):
    lb = forms.IntegerField(required=True,help_text='For 70-100 enter 70 ')
    grade = forms.CharField(required=True,help_text='1 or A ')
    remark= forms.TextInput()

    class Meta:
        fields=['lb','grade','remark']
        model = models.OverallGradebook

class SaveOverallGradebook(forms.ModelForm):
   
    lb = forms.IntegerField(required=True,help_text='For 70-100 enter 70 ')
    grade = forms.CharField(required=True,help_text='A ')
    remark= forms.TextInput()


    class Meta:
        fields=['lb','grade','remark']
        model = models.OverallGradebook

    def clean_grade(self):
        id = int(self.data['id']) if (self.data['id']).isnumeric() else 0
        grade = self.cleaned_data['grade']
        try:
            if id > 0:
                gradebook = models.OverallGradebook.objects.exclude(id = id).get(grade = grade)
            else:
                gradebook = models.OverallGradebook.objects.get(grade = grade)
        except:
            return grade
        raise forms.ValidationError("Id already exists on the Database.")
  

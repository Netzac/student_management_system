from datetime import datetime
from email.policy import default
from django import forms 
from django.core import validators
from django.forms import Form,ModelForm, modelformset_factory, inlineformset_factory
from django.forms.widgets import NumberInput
from pytz import timezone  
from django.utils import timezone as timeZ
from student_core.models import (
    ClassTeacher, Courses, SessionYearModel, 
    AcademicTerm,Gender, ConductInterestRemarks,)

from student_exam.models import Exercise


class DateInput(forms.DateInput):
    input_type = "date"

mobile_num_regex = validators.RegexValidator(
        regex="^[0-9]{10,15}$", message="Invalid Contact Number format! Must be between 10 and 15 digits")

'''Parents data'''
class AddStudentForm(forms.Form):

    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    dob = forms.DateField(label="Date of Birth",widget = NumberInput(attrs={'type':'date'}),initial=timeZ.now)
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
   
    email = forms.EmailField(validators=[validators.EmailValidator(message='Invalid email format')],label="Email",  max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
   
    #For Displaying Courses
    try:
        courses = Courses.objects.all()
        course_list = []
        for course in courses:
            single_course = (course.id, course.course_name)
            course_list.append(single_course)
    except:
        course_list = []
    
    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []
    

    #For Displaying Genders
    try:
        genders = Gender.objects.all()
        gender_list = []
        for gender in genders:
            single_gender = (gender.id, gender.gender_name)
            gender_list.append(single_gender)
           # print("gender_list :",gender_list)
    except:
        gender_list = []
    # gender_list = (
    #     ('Male','Male'),
    #     ('Female','Female')
    # )
    
    course_id = forms.ChoiceField(label="Class", choices=course_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender_id = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Picture", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

  
    parent_first_name = forms.CharField(label="Parent First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_last_name = forms.CharField(label="Parent Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_email = forms.CharField(validators=[validators.EmailValidator(message='Invalid email format')],label="Parent Email", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_contact_number = forms.CharField(validators=[mobile_num_regex],label="Parent Contact Number", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_occupation = forms.CharField(label="Parent Occupation", max_length=255, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    

class EditStudentForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    dob = forms.DateField(label="Date of Birth",widget = NumberInput(attrs={'type':'date'}),initial=timeZ.now)
    email = forms.EmailField(validators=[validators.EmailValidator(message='Invalid email format')],label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
   
    #For Displaying Courses
    gender_list = []
    try:
        courses = Courses.objects.all()
        course_list = []
        for course in courses:
            single_course = (course.id, course.course_name)
            course_list.append(single_course)
    except:
        course_list = []

    #For Displaying Session Years
    try:
        session_years = SessionYearModel.objects.all()
        session_year_list = []
        for session_year in session_years:
            single_session_year = (session_year.id, str(session_year.session_start_year)+" to "+str(session_year.session_end_year))
            session_year_list.append(single_session_year)
            
    except:
        session_year_list = []

    
     #For Displaying Genders
    try:
        genders = Gender.objects.all()
        gender_list = []
        for gender in genders:
            single_gender = (gender.id, gender.gender_name)
            gender_list.append(single_gender)
           # print("gender_list :",gender_list)
    except:
        gender_list = []
    
    course_id = forms.ChoiceField(label="Course", choices=course_list, widget=forms.Select(attrs={"class":"form-control"}))
    gender_id = forms.ChoiceField(label="Gender", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", choices=session_year_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start_year = forms.DateField(label="Session Start", widget=DateInput(attrs={"class":"form-control"}))
    # session_end_year = forms.DateField(label="Session End", widget=DateInput(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

    '''Parents data'''
    parent_first_name = forms.CharField(label="Parent First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_last_name = forms.CharField(label="Parent Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_email = forms.CharField(validators=[validators.EmailValidator(message='Invalid email format')],label="Parent Email", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_contact_number = forms.CharField(validators=[mobile_num_regex],label="Parent Contact Number", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    parent_occupation = forms.CharField(label="Parent Occupation", max_length=255, widget=forms.TextInput(attrs={"class":"form-control"}))


    
''' Addition forms'''

class AcademicTermForm(ModelForm):
    prefix = "Academic Term"

    class Meta:
        model = AcademicTerm
        fields = ["name", "current"]


class CurrentSessionForm(forms.Form):
    current_session = forms.ModelChoiceField(
        queryset=SessionYearModel.objects.all(),
        help_text='Click <a href="/add_session/">here</a> to add new session',
    )
    current_term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        help_text='Click <a href="/term/create/?next=current-session/">here</a> to add new term',
    )

class ExerciseForm(ModelForm):
    prefix = "Exercise"

    class Meta:
        model = Exercise
        fields = ["name"]
        
ClassTeacherFormSet = modelformset_factory(
    ClassTeacher,fields=('staff_id','cls_id'),can_delete=True,extra=0
)


ConductInterestRemarksFormset = modelformset_factory(
    ConductInterestRemarks,fields=('conduct','interest','remarks'),can_delete=True,extra=0
)

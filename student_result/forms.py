from django import forms
from django.forms import modelformset_factory

from student_core.models import SessionYearModel as AcademicSession, AcademicTerm, Subjects as Subject

from .models import Result,ClassExercise
from student_core.models import Courses,Students


class CreateResults(forms.Form):
    session = forms.ModelChoiceField(queryset=AcademicSession.objects.all())
    term = forms.ModelChoiceField(queryset=AcademicTerm.objects.all())
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple
    )


EditResults = modelformset_factory(
    Result, fields=("test_score", "exam_score"), extra=0, can_delete=True,can_order=True
)

EditExResults = modelformset_factory(
    ClassExercise, fields=("score",), extra=0, can_delete=True,can_order=True
)

class FindResultForm(forms.ModelForm):

    class Meta:
        model = Result
        fields = ('student','current_class')

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['student'].queryset = Students.objects.none
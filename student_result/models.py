from django.db import models

# Create your models here.

from student_core.models import (
    SessionYearModel as AcademicSession,
    AcademicTerm,
    Courses as StudentClass,
    Subjects as Subject,
)
from student_core.models import Students as Student

from .utils import score_grade


# Create your models here.
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    current_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test_score = models.IntegerField(default=0)
    exam_score = models.IntegerField(default=0)

    class Meta:
        ordering = ["subject"]

    def __str__(self):
        return f"{self.student} {self.session} {self.term} {self.subject}"

    def total_score(self):
        return self.test_score + self.exam_score

    def grade(self):
        return score_grade(self.total_score())



from student_exam.models import Exercise
class ClassExercise(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    current_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    exercise= models.ForeignKey(Exercise,on_delete=models.CASCADE)
    score= models.ImageField()

    class meta:
        ordering=['exercise']

    def __str__(self):
        return self.score
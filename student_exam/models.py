

from enum import auto
from typing_extensions import Required
import uuid
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from student_core.models import CustomUser as User

def unique_passcode():
    d = uuid.uuid4()
    passcode = d.hex
    return passcode[0:8]


from student_core.models import (CustomUser as User,Courses, SessionYearModel, Students, Subjects, 

)

class Exercise(models.Model):
    name= models.CharField(max_length=15)
    objects=models.Manager()

    class meta:
        ordering=['name']

    def __str__(self):
        return self.name

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    passcode = models.CharField(max_length=100, default= unique_passcode)
    content = models.TextField()
    upload = models.FileField(upload_to='assignments/', default="")
    due_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    course = models.ForeignKey(Courses, verbose_name="Class",on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subjects,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name='assignments'
    )

    objects = models.Manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("assignment-detail", kwargs={"id": self.pk})

class Submission(models.Model):
    matric_number = models.CharField(max_length=100,default= unique_passcode)
    upload = models.FileField(upload_to='submissions/')
    answer = models.TextField(null=True,blank=True,default="None")
    submitted_at = models.DateField(auto_now=True)
    last_updated = models.DateField(auto_now=True)
    assignment = models.ForeignKey(Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    grade = models.CharField(max_length=100, null=True, blank=True, default="No grade yet")
    feedback = models.CharField(max_length=255, null=True, blank=True, default="No feedback yet")


class Gradebook(models.Model):
    lb = models.IntegerField()
    grade = models.CharField(max_length=15)
    remark = models.CharField(max_length=50)
    date_added=models.DateTimeField(auto_now=True)

    class meta:
        ordering=['-lb']
    def __str__(self):
        return self.grade


class OverallGradebook(models.Model):
    lb = models.IntegerField()
    grade = models.CharField(max_length=15)
    remark = models.CharField(max_length=50)
    date_added=models.DateTimeField(auto_now=True)

    class meta:
        ordering=['-lb']
    def __str__(self):
        return self.grade





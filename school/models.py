from typing_extensions import Required
from django.db import models
from django.urls import reverse
import uuid

# Create your models here.


from student_core.models import CustomUser as User

def unique_school_id():
    d = uuid.uuid4()
    schid = d.hex
    return schid[0:15]

class School(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False,verbose_name="School Name")
    motto =  models.CharField(max_length=255,null=True,blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField(null=False,blank=False)
    branch = models.CharField(max_length=255,null=True,blank=True)
    admin = models.OneToOneField(User, on_delete = models.CASCADE, default=1)
    adminSignature = models.FileField(upload_to="school/",null=True,blank=True)
    logo = models.FileField(upload_to="school/",null=True,blank=True)
    seal = models.FileField(upload_to="school/",null=True,blank=True)
    school_id = models.CharField(max_length=20,default=unique_school_id)


    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse('school-list')

    def __str__(self):
        return f"{self.name}"


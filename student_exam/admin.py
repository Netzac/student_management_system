from django.contrib import admin

from student_exam.models import Assignment, Submission

# Register your models here.
admin.site.register(Assignment)
admin.site.register(Submission)
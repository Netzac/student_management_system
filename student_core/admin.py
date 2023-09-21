from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (AcademicTerm, CustomUser, AdminHOD, SessionYearModel, 
Staffs, Courses, Subjects, Students,
 Attendance, AttendanceReport, LeaveReportStudent, LeaveReportStaff, 
 FeedBackStudent, FeedBackStaffs, NotificationStudent, NotificationStaffs,)
from student_account.models import FeeType, Invoice, InvoiceItem, Payroll,Staff_Deductions,Staff_Earnings
# Register your models here.
class UserModel(UserAdmin):
    pass


admin.site.register(CustomUser, UserModel)

admin.site.register(AdminHOD)
admin.site.register(Staffs)
admin.site.register(Courses)
admin.site.register(Subjects)
admin.site.register(Students)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportStudent)
admin.site.register(LeaveReportStaff)
admin.site.register(FeedBackStudent)
admin.site.register(FeedBackStaffs)
admin.site.register(NotificationStudent)
admin.site.register(NotificationStaffs)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(FeeType)
admin.site.register(SessionYearModel)
admin.site.register(AcademicTerm)

admin.site.register(Payroll)
admin.site.register(Staff_Deductions)
admin.site.register(Staff_Earnings)


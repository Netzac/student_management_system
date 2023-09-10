import profile
from re import template
from urllib.request import Request
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from django.db import models

from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from student_account.forms import FeeTypeForm

from student_core.models import (ClassTeacher, CustomUser, Staffs, Courses, Subjects, Gender,
Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, 
LeaveReportStudent, LeaveReportStaff, Attendance,
 AttendanceReport, AcademicTerm,
)
from .forms import (AddStudentForm, ClassTeacherFormSet, ClassTeacherFormSet, EditStudentForm,
 AcademicTermForm, CurrentSessionForm, ExerciseForm)
from student_account.forms import FeeTypeForm
from student_account.models import FeeType

from student_exam.models import Exercise

from student_result.utils import get_teacher_cls_id


def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.all().count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        #course = Courses.objects.get(id=subject.course_id.id)
        course = Courses.objects.all()
        #student_count = Students.objects.filter(course_id=course.id).count()
        student_count = Students.objects.all().count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        #subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        #class_ids = Subjects.objects.filter(staff_id=staff.admin.id).values('course_id')
        class_ids = Courses.objects.all().values('id')
        attendance = Attendance.objects.filter(course_id__in=class_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)

    '''For Gender Distribution'''
    from django.db.models import Count
    gender_obj = Gender.objects.all()
    gender_list = [gender.gender_name for gender in gender_obj]
  
    print("Gender list :", gender_list)
    gender_count = []
    gender_distr = Students.objects.values("gender").annotate(g_count=Count("id"))
    gender_count = [gender['g_count'] for gender in gender_distr]
    diff = len(gender_list)-len(gender_count)
    extra = [0]*diff
    gender_count.extend(extra)

    print("Gender_distr:", gender_count)

    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
        "gender_list":gender_list,
        "gender_list_count":gender_count
    }
    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    gender = Gender.objects.all()
    context ={'genders': gender}
    return render(request, "hod_template/add_staff_template.html",context)


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

          # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
        if len(request.FILES) != 0:
            signature = request.FILES['signature']
            fs = FileSystemStorage('media/signature/')
            filename = fs.save(signature.name, signature)
            signature_url = fs.url(filename)
        else:
            signature_url = None

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.staffs.signature=signature_url
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        if len(request.FILES) != 0:
            signature = request.FILES['signature']
            fs = FileSystemStorage('media/signature/')
            filename = fs.save(signature.name, signature)
            signature_url = (fs.url(filename)).replace("media",'signature')
            print("filename:",signature_url)
        else:
            signature_url = None

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.signature= signature_url
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')




def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Class Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Class!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')

### Adding  Gender Setups for inclusivity suggested by Prudhvi ###

def add_gender(request):
    return render(request, "hod_template/add_gender_template.html")


def add_gender_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_gender')
    else:
        gender = request.POST.get('gender')
        try:
            gender_model = Gender(gender_name=gender)
            gender_model.save()
            messages.success(request, "Gender Added Successfully!")
            return redirect('add_gender')
        except:
            messages.error(request, "Failed to Add Gender!")
            return redirect('add_gender')


def manage_gender(request):
    genders = Gender.objects.all()
    context = {
        "genders": genders
    }
    return render(request, 'hod_template/manage_gender_template.html', context)


def edit_gender(request, gender_id):
    gender = Gender.objects.get(id=gender_id)
    context = {
        "gender": gender,
        "id": gender_id
    }
    return render(request, 'hod_template/edit_gender_template.html', context)


def edit_gender_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        gender_id = request.POST.get('gender_id')
        gender_name = request.POST.get('gender')

        try:
            gender = Gender.objects.get(id=gender_id)
            gender.gender_name = gender_name
            gender.save()

            messages.success(request, "Gender Updated Successfully.")
            return redirect('/edit_gender/'+ gender_id)

        except:
            messages.error(request, "Failed to Update Gender.")
            return redirect('/edit_gender/'+ gender_id)


def delete_gender(request, gender_id):
    gender = Gender.objects.get(id=gender_id)
    try:
        gender.delete()
        messages.success(request, "Gender Deleted Successfully.")
        return redirect('manage_gender')
    except:
        messages.error(request, "Failed to Delete Gender.")
        return redirect('manage_gender')


### End of Adding Gender ####

def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')
        name = request.POST.get('session')
        current = True if(request.POST.get('current')) else False
        re_opening_date = request.POST.get('re_opening_date')
        #print(session_end_year)
        #print(name)
        #print(current)


        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, 
            session_end_year=session_end_year, name=name,current=current,re_opening_date=re_opening_date)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    print('Session Year',session_year.re_opening_date)
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')
        re_opening_date = request.POST.get('re_opening_date')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.re_opening_date = re_opening_date
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['course_id']
            gender_id = form.cleaned_data['gender_id']
            dob = form.cleaned_data['dob']

            parent_first_name = form.cleaned_data['parent_first_name']
            parent_last_name = form.cleaned_data['parent_last_name']
            parent_email = form.cleaned_data['parent_email']
            parent_occupation = form.cleaned_data['parent_occupation']
            parent_contact_number = form.cleaned_data['parent_contact_number']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(f"student/{profile_pic.name}", profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                fs = FileSystemStorage()
                filename ="default.jpg"
                profile_pic_url = fs.url(filename)


            # try:
            #print("Gender is :", gender_id)
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
           # print("obhect :",user.username)
            user.students.address = address
            course_obj = Courses.objects.get(id=course_id)
            user.students.course_id = course_obj

            session_year_obj = SessionYearModel.objects.get(id=session_year_id)
            user.students.session_year_id = session_year_obj
           
            gender_obj = Gender.objects.get(id=gender_id)
           
            user.students.gender = gender_obj
            user.students.dob = dob
            user.students.profile_pic = profile_pic_url

            user.students.parent_first_name =parent_first_name
            user.students.parent_last_name =parent_last_name
            user.students.parent_email = parent_email
            user.students.parent_occupation =parent_occupation
            user.students.parent_contact_number = parent_contact_number
            
            user.save()
            messages.success(request, "Student Added Successfully!")
            return redirect('add_student')
            # except:
            #     messages.error(request, "Failed to Add Student!")
            #     return redirect('add_student')
        else:
            messages.error(request, "Invalid Inputs! Please, see error descriptions above!")
            context = {"form": form}
            return render(request, 'hod_template/add_student_template.html', context)
            #return redirect('add_student')


def manage_student(request):
    user_type = request.user.user_type
   
    students = Students.objects.all()

    if user_type=='2':
        students= students.filter(course_id = get_teacher_cls_id(request))
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['dob'].initial = student.dob
    form.fields['course_id'].initial = student.course_id.id
    form.fields['gender_id'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id.id
    form.fields['parent_first_name'].initial =student.parent_first_name
    form.fields['parent_last_name'].initial =student.parent_last_name
    form.fields['parent_email'].initial = student.parent_email
    form.fields['parent_occupation'].initial = student.parent_occupation
    form.fields['parent_contact_number'].initial = student.parent_contact_number

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            dob = form.cleaned_data['dob']
            course_id = form.cleaned_data['course_id']
            gender_id = form.cleaned_data['gender_id']
            session_year_id = form.cleaned_data['session_year_id']

            parent_first_name = form.cleaned_data['parent_first_name']
            parent_last_name = form.cleaned_data['parent_last_name']
            parent_email = form.cleaned_data['parent_email']
            parent_occupation = form.cleaned_data['parent_occupation']
            parent_contact_number = form.cleaned_data['parent_contact_number']


            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(f"student/{profile_pic.name}", profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            #try:
                # First Update into Custom User Model
            user = CustomUser.objects.get(id=student_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            # Then Update Students Table
            student_model = Students.objects.get(admin=student_id)
            student_model.address = address

            course = Courses.objects.get(id=course_id)
            student_model.course_id = course

            session_year_obj = SessionYearModel.objects.get(id=session_year_id)
            student_model.session_year_id = session_year_obj
            gender_obj = Gender.objects.get(id=gender_id)
            student_model.gender_id = gender_obj
            student_model.dob = dob

            student_model.parent_first_name =parent_first_name
            student_model.parent_last_name =parent_last_name
            student_model.parent_email = parent_email
            student_model.parent_occupation =parent_occupation
            student_model.parent_contact_number = parent_contact_number

            if profile_pic_url != None:
                student_model.profile_pic = profile_pic_url
            student_model.save()
            # Delete student_id SESSION after the data is updated
            del request.session['student_id']

            messages.success(request, "Student Updated Successfully!")
            return redirect('/edit_student/'+student_id)
            # except:
            #     messages.error(request, "Failed to Update Student.")
            #     return redirect('/edit_student/'+student_id)
        else:
            #return redirect('/edit_student/'+student_id)
            student = Students.objects.get(admin=student_id)
            context = {
            "id": student_id,
            "username": student.admin.username,
            "form": form
            }
            return render(request, "hod_template/edit_student_template.html", context)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_subject(request):
    #courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
    
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        #course_id = request.POST.get('course')
        #course = Courses.objects.get(id=course_id)
        
        # staff_id = request.POST.get('staff')
        # staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('manage_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    #courses = Courses.objects.all()
    # staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
     #   course_id = request.POST.get('course')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

           # course = Courses.objects.get(id=course_id)
           # subject.course_id = course
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    user_type = request.user.user_type
    template_name = "hod_template/admin_view_attendance.html"
    if user_type=='1':
        classes = Courses.objects.all()
        session_years = SessionYearModel.objects.all()
        context = {
            "classes": classes,
            "session_years": session_years
        }
    elif user_type=='2':
        template_name = "staff_template/staff_view_attendance.html"
        clsid = request.user.staffs.classteacher.cls_id.id
        classes = Courses.objects.filter(id=clsid)
        session_years = SessionYearModel.objects.all()
        context = {
            "classes": classes,
            "session_years": session_years
        }
    return render(request, template_name, context)


from django.views.decorators.csrf import requires_csrf_token

@requires_csrf_token
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    cls_id = request.POST.get("cls")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    cls_model = Courses.objects.get(id=cls_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(course_id=cls_id, session_year_id=session_year).distinct('attendance_date')

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


#@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date).attendance_date

    attendance_data = Attendance.objects.filter(attendance_date=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def staff_profile(request):
    pass


def student_profile(requtest):
    pass


'''Additional Views''' 
class TermListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicTerm
    template_name = "hod_template/term_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicTermForm()
        return context

class TermCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("terms")
    success_message = "New term successfully added"
    


class TermUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    success_url = reverse_lazy("terms")
    success_message = "Term successfully updated."
    template_name = "hod_template/mgt_form.html"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicTerm.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a term to current.")
                return redirect("term")
        return super().form_valid(form)


class TermDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicTerm
    success_url = reverse_lazy("terms")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The term {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete term as it is set to current")
            return redirect("terms")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(TermDeleteView, self).delete(request, *args, **kwargs)




class CurrentSessionAndTermView(LoginRequiredMixin, View):
    """Current SEssion and Term"""

    form_class = CurrentSessionForm
    template_name = "hod_template/current_session.html"
    success_message = "This {} has been set as the current session"

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            initial={
                "current_session": SessionYearModel.objects.get(current=True),
                "current_term": AcademicTerm.objects.get(current=True),
            }
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            session = form.cleaned_data["current_session"]
            term = form.cleaned_data["current_term"]
            newCurr = SessionYearModel.objects.get(name=session) #.update(current=True)
            newCurr.current = True
            newCurr.save()
            oldCurr = SessionYearModel.objects.exclude(name=session).update(current=False)
            #oldCurr.current=False
            #oldCurr.save()
            newTerm = AcademicTerm.objects.get(name=term) #.update(current=True)
            newTerm.current=True
            newTerm.save()
            AcademicTerm.objects.exclude(name=term).update(current=False)

        
        messages.success(self.request, self.success_message.format(session))
        return render(request, self.template_name, {"form": form})


# Attendance HOD Views

@login_required
def attendance(request):
    user_type =request.user.user_type
    template_name = 'hod_template/attendance.html'
    if user_type=='1':
        classes = Courses.objects.all() #get_object_or_404(Courses)
        return render(request,template_name, {'classes': classes})
    elif user_type=='2':
        cls_id = request.user.staffs.classteacher.cls_id.id
        template_name = 'staff_template/attendance.html'
        classes =get_object_or_404(Courses,id=cls_id) #get_object_or_404(Courses)
        return render(request,template_name, {'classes': classes})

@login_required()
def attendance_class(request, cls_id):
    user_type =request.user.user_type
    cls = get_object_or_404(Courses, id=cls_id)
    template_name =  'hod_template/attendance_class.html'

    if user_type=='2':
        template_name =  'staff_template/attendance_class.html'

    context = {
        'cls': cls
        
    }
    return render(request,template_name, context)


@login_required()
def take_attendance(request, cls_id):
    #print('Currrent Session:',request.POST)
    session_year_id =  SessionYearModel.objects.get(current=True)
    
    cls = get_object_or_404(Courses, id=cls_id)
    for i, s in enumerate(cls.students_set.all()):
        status = request.POST.get(str(s.id))
        print('Status is :',status, i, s.id,request.POST)
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        date = request.POST['date']
        a = Attendance(course_id=cls, student_id=s, status=status, attendance_date=date, session_year_id=session_year_id)
        a.save()
    messages.success(request,"Attendance successfully taken")
    return HttpResponseRedirect(reverse('attendance'))


class ClassTeacherAddView(SuccessMessageMixin,LoginRequiredMixin, CreateView):
    model= ClassTeacher
    #fields=['staff_id','cls_id']
    form_class = ClassTeacherFormSet
    template_name="hod_template/class_teacher_form.html"
    error_message ="Class to Teacher combination not allowed"
    success_message = 'Item successfully added.'

    def get(self,*args,**kwargs):
        # staffs = Staffs.objects.all().values('id')
        # classes = Courses.objects.all().values('id')
        formset=ClassTeacherFormSet(initial=[{"staff_id":"0"},{"cls_id":"0"}],queryset=ClassTeacher.objects.all())
        return self.render_to_response({"class_teacher_formset":formset})

    def post(self,*args,**kwargs):
        formset= ClassTeacherFormSet(data=self.request.POST)
        print('formset: ',self.request.POST,formset.errors)
        print('erros: ',formset.errors)
        if formset.is_valid():
            formset.save()
            return redirect(reverse_lazy("class_teacher_list"))
        return self.render_to_response({"class_teacher_formset":formset})
  
class ClassTeacherListView(ListView):
    model=ClassTeacher
    template_name="hod_template/class_teacher_list.html"


class CTUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ClassTeacher
    form_class = ClassTeacherFormSet
    success_url = reverse_lazy("class_teacher_list")
    success_message = "Item successfully updated."

    
   # template_name = "hod_template/mgt_form.html"



class CTDeleteView(LoginRequiredMixin, DeleteView):
    model = ClassTeacher
    success_url = reverse_lazy("class_teacher_list")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The term {} has been deleted with all its attached content"
   

'''Class Exercise HOD Views'''
class ExerciseListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Exercise
    template_name = "hod_template/exercise_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ExerciseForm()
        return context

class ExerciseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = "hod_template/mgt_form.html"
    success_url = reverse_lazy("exercises")
    success_message = "New Exercise successfully added"
    


class ExerciseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    success_url = reverse_lazy("exercises")
    success_message = "Exercise successfully updated."
    template_name = "hod_template/mgt_form.html"


class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    model = Exercise
    success_url = reverse_lazy("exercises")
    template_name = "hod_template/core_confirm_delete.html"
    success_message = "The exercise {} has been deleted"

import datetime
def get_birthdays(request):
    birthdays=Students.objects.filter(dob__day=datetime.date.today().day,dob__month=datetime.date.today().month).order_by('course_id') #.exclude(birthday__year=1)
    return render(request, 'hod_template/birthday_list.html', {'birthdays': birthdays})



from django.views.generic import DetailView
class StudentDetailView(LoginRequiredMixin, DetailView):
    template_name = 'hod_template/student_detail.html'
    model = Students
    fields = "__all__"

    def get_context_data(self, **kwargs):
        context = super(StudentDetailView, self).get_context_data(**kwargs)
        return context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
import datetime # To Parse input DateTime into Python Date Time Object

from student_core.models import CustomUser, Staffs, Courses, Subjects, Students, Attendance, AttendanceReport, LeaveReportStudent, FeedBackStudent, StudentResult, Event, RSVP, TimetableEntry, SessionYearModel, AcademicTerm, TimeSlot
from school.models import School
from .forms import RSVPForm
from django.contrib.auth.decorators import login_required


def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()

    course_obj = Courses.objects.get(id=student_obj.course_id.id)
    total_subjects = Subjects .objects.all().count()
    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.all()
    for subject in subject_data:
        attendance = Attendance.objects.all()
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    
    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "total_subjects": total_subjects,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "student_template/student_home_template.html", context)


def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id) # Getting Logged in Student Data
    course = student.course_id # Getting Course Enrolled of LoggedIn Student
    # course = Courses.objects.get(id=student.course_id.id) # Getting Course Enrolled of LoggedIn Student
    subjects = Subjects.objects.all() #filter(course_id=course) # Getting the Subjects of Course Enrolled
    context = {
        "subjects": subjects
    }
    return render(request, "student_template/student_view_attendance.html", context)


def student_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_view_attendance')
    else:
        # Getting all the Input Data
        #subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Getting all the Subject Data based on Selected Subject
            #subject_obj = Subjects.objects.get(id=subject_id)
        # Getting Logged In User Data
        user_obj = CustomUser.objects.get(id=request.user.id)
        # Getting Student Data Based on Logged in Data
        stud_obj = Students.objects.get(admin=user_obj)

        # Now Accessing Attendance Data based on the Range of Date Selected and Subject Selected
        attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse),student_id=stud_obj)
        # Getting Attendance Report based on the attendance details obtained above
        #attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

        # for attendance_report in attendance_reports:
        #     print("Date: "+ str(attendance_report.attendance_id.attendance_date), "Status: "+ str(attendance_report.status))

        # messages.success(request, "Attendacne View Success")

        context = {
            "student":stud_obj,
            "attendance_reports": attendance
        }

        return render(request, 'student_template/student_attendance_data.html', context)
       

def student_apply_leave(request):
    student_obj = Students.objects.get(admin=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
    context = {
        "leave_data": leave_data
    }
    return render(request, 'student_template/student_apply_leave.html', context)


def student_apply_leave_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_apply_leave')
    else:
        leave_date = request.POST.get('leave_date')
        leave_message = request.POST.get('leave_message')

        student_obj = Students.objects.get(admin=request.user.id)
        try:
            leave_report = LeaveReportStudent(student_id=student_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('student_apply_leave')
        except:
            messages.error(request, "Failed to Apply Leave")
            return redirect('student_apply_leave')


def student_feedback(request):
    student_obj = Students.objects.get(admin=request.user.id)
    feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'student_template/student_feedback.html', context)


def student_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('student_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        student_obj = Students.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStudent(student_id=student_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('student_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('student_feedback')


def student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Students.objects.get(admin=user)

    context={
        "user": user,
        "student": student
    }
    return render(request, 'student_template/student_profile.html', context)


def student_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('student_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            student = Students.objects.get(admin=customuser.id)
            student.address = address
            student.save()
            
            messages.success(request, "Profile Updated Successfully")
            return redirect('student_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('student_profile')


def student_view_result(request):
    student = Students.objects.get(admin=request.user.id)
    student_result = StudentResult.objects.filter(student_id=student.id)
    context = {
        "student_result": student_result,
    }
    return render(request, "student_template/student_view_result.html", context)


@login_required
def student_id_card(request):
    student = Students.objects.get(admin=request.user.id)
    school = School.objects.first()
    context = {
        'student': student,
        'school': school,
        'now': datetime.datetime.now()
    }
    return render(request, 'student_template/student_id_card.html', context)


# Student Event Views
@login_required
def student_event_list(request):
    events = Event.objects.all().order_by('-start_date')
    # Get all user's RSVPs for quick lookup
    user_rsvps = RSVP.objects.filter(user=request.user).values_list('event_id', flat=True)
    # Create a dictionary of event_id: rsvp_status
    user_rsvp_map = {rsvp.event_id: rsvp for rsvp in RSVP.objects.filter(user=request.user)}
    context = {
        'events': events,
        'user_rsvp_map': user_rsvp_map
    }
    return render(request, 'student_template/event_list.html', context)


@login_required
def student_event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    # Get existing RSVP if any
    existing_rsvp = RSVP.objects.filter(event=event, user=request.user).first()
    
    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=existing_rsvp)
        if form.is_valid():
            rsvp = form.save(commit=False)
            rsvp.user = request.user
            rsvp.event = event
            rsvp.save()
            messages.success(request, 'Your RSVP has been saved!')
            return redirect('student_event_detail', pk=pk)
    else:
        form = RSVPForm(instance=existing_rsvp)
    
    context = {
        'event': event,
        'form': form,
        'rsvp': existing_rsvp
    }
    return render(request, 'student_template/event_detail.html', context)







@login_required
def student_timetable_view(request):
    """View to display student's timetable in a grid format"""
    student = Students.objects.get(admin=request.user.id)
    session_years = SessionYearModel.objects.all()
    terms = AcademicTerm.objects.all()
    
    selected_session = request.GET.get('session_year')
    selected_term = request.GET.get('term')
    
    timetable_entries = TimetableEntry.objects.filter(course=student.course_id)
    if selected_session:
        timetable_entries = timetable_entries.filter(session_year_id=selected_session)
    if selected_term:
        timetable_entries = timetable_entries.filter(term_id=selected_term)
    
    # Organize entries by day
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timetable_data = {day: [] for day in days}
    for entry in timetable_entries:
        timetable_data[entry.time_slot.day].append(entry)
    
    # Organize time slots
    time_slots = TimeSlot.objects.all().order_by('day', 'start_time')
    
    context = {
        'session_years': session_years,
        'terms': terms,
        'selected_session': selected_session,
        'selected_term': selected_term,
        'timetable_data': timetable_data,
        'time_slots': time_slots,
    }
    
    return render(request, 'student_template/timetable_view.html', context)

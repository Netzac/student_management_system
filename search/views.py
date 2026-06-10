from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from bookstore.models import Book
from student_core.models import Students, Staffs, Subjects, Courses


# Define all sidebar menu items
SIDEBAR_MENU_ITEMS = [
    # Home
    {'type': 'Menu', 'text': 'Home', 'url_name': 'admin_home', 'category': 'Dashboard'},
    # Person Registry
    {'type': 'Menu', 'text': 'Staff', 'url_name': 'manage_staff', 'category': 'Person Registry'},
    {'type': 'Menu', 'text': 'Staff Inbox', 'url_name': 'staff_feedback_message', 'category': 'Person Registry'},
    {'type': 'Menu', 'text': 'Staff Leave', 'url_name': 'staff_leave_view', 'category': 'Person Registry'},
    {'type': 'Menu', 'text': 'Student', 'url_name': 'manage_student', 'category': 'Person Registry'},
    {'type': 'Menu', 'text': 'Students Inbox', 'url_name': 'student_feedback_message', 'category': 'Person Registry'},
    {'type': 'Menu', 'text': 'Student Leave', 'url_name': 'student_leave_view', 'category': 'Person Registry'},
    # Students Results
    {'type': 'Menu', 'text': 'Class Exercise Entry', 'url_name': 'ex-result-class', 'category': 'Students Results'},
    {'type': 'Menu', 'text': 'Exam Results Entry', 'url_name': 'select-result-class', 'category': 'Students Results'},
    {'type': 'Menu', 'text': 'Conduct Interest Entry', 'url_name': 'cir-class', 'category': 'Students Results'},
    {'type': 'Menu', 'text': 'Term Reports', 'url_name': 'find-result', 'category': 'Students Results'},
    {'type': 'Menu', 'text': 'Promote Students', 'url_name': 'promote-students', 'category': 'Students Results'},
    # Students Assignments
    {'type': 'Menu', 'text': 'Assignments Dashboard', 'url_name': 'dashboard', 'category': 'Students Assignments'},
    # Attendance Module
    {'type': 'Menu', 'text': 'Attendance Sheet', 'url_name': 'attendance', 'category': 'Attendance Module'},
    {'type': 'Menu', 'text': 'Attendance Report', 'url_name': 'admin_view_attendance', 'category': 'Attendance Module'},
    # School Settings
    {'type': 'Menu', 'text': 'Enter School Details', 'url_name': 'school-create', 'category': 'School Settings'},
    {'type': 'Menu', 'text': 'View School Details', 'url_name': 'school-list', 'category': 'School Settings'},
    # General Settings
    {'type': 'Menu', 'text': 'Bank', 'url_name': 'bank-list', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Class', 'url_name': 'manage_course', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Class To Teacher Mapping', 'url_name': 'add_class_teacher', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Manage CT Mapping', 'url_name': 'class_teacher_list', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Class Exercises', 'url_name': 'exercises', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Deductions', 'url_name': 'deductions-list', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Earnings', 'url_name': 'earnings-list', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Gender', 'url_name': 'manage_gender', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Subject Grade Book', 'url_name': 'gradebook', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Overall Grade Book', 'url_name': 'overall-gradebook', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Role/Designation', 'url_name': 'role-list', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Session', 'url_name': 'manage_session', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Subject', 'url_name': 'manage_subject', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Tax Table', 'url_name': 'taxtable', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Terms', 'url_name': 'terms', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Fee Types', 'url_name': 'feetype-list', 'category': 'General Settings'},
    {'type': 'Menu', 'text': 'Stationery', 'url_name': 'store:stationery-list', 'category': 'General Settings'},
    # Accounts
    {'type': 'Menu', 'text': 'Accounts Dashboard', 'url_name': 'account-dashboard', 'category': 'Accounts'},
    {'type': 'Menu', 'text': 'Payroll', 'url_name': 'payroll-list', 'category': 'Accounts'},
    {'type': 'Menu', 'text': 'Student Bills', 'url_name': 'invoice-list', 'category': 'Accounts'},
    {'type': 'Menu', 'text': 'Bulk SMS', 'url_name': 'bulk-sms', 'category': 'Accounts'},
    {'type': 'Menu', 'text': 'Reports By Date Range', 'url_name': 'report-by-range', 'category': 'Accounts Reports'},
    {'type': 'Menu', 'text': 'Reports By Month', 'url_name': 'report-by-month', 'category': 'Accounts Reports'},
    # Library
    {'type': 'Menu', 'text': 'Library Dashboard', 'url_name': 'lib:dashboard', 'category': 'Library'},
    # Book Store
    {'type': 'Menu', 'text': 'Store Place', 'url_name': 'store:index', 'category': 'Book Store'},
    {'type': 'Menu', 'text': 'Class Requirements', 'url_name': 'store:requireditem-class', 'category': 'Book Store'},
    {'type': 'Menu', 'text': 'Requirements Lists', 'url_name': 'store:requireditem-list', 'category': 'Book Store'},
]


def search(request):
    search_query = request.GET.get('q', '')
    results = {
        'students': [],
        'staff': [],
        'subjects': [],
        'courses': [],
        'bookstore_books': [],
        'menu_items': [],
    }

    if search_query:
        # Search Students
        results['students'] = Students.objects.filter(
            Q(admin__first_name__icontains=search_query) |
            Q(admin__last_name__icontains=search_query) |
            Q(admin__username__icontains=search_query)
        ).select_related('admin', 'course_id')

        # Search Staff
        results['staff'] = Staffs.objects.filter(
            Q(admin__first_name__icontains=search_query) |
            Q(admin__last_name__icontains=search_query) |
            Q(admin__username__icontains=search_query)
        ).select_related('admin', 'role')

        # Search Subjects
        results['subjects'] = Subjects.objects.filter(
            Q(subject_name__icontains=search_query)
        )

        # Search Courses (Classes)
        results['courses'] = Courses.objects.filter(
            Q(course_name__icontains=search_query)
        )

        # Search Bookstore Books
        results['bookstore_books'] = Book.objects.filter(
            Q(title__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(author__icontains=search_query)
        )

        # Search Menu Items
        results['menu_items'] = [
            item for item in SIDEBAR_MENU_ITEMS
            if search_query.lower() in item['text'].lower()
        ]

    context = {
        'search_query': search_query,
        'results': results,
    }
    return render(request, 'search/results.html', context)


def autocomplete(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        # Menu Items First
        menu_items = [
            item for item in SIDEBAR_MENU_ITEMS
            if query.lower() in item['text'].lower()
        ][:10]
        for item in menu_items:
            try:
                url = reverse(item['url_name'])
            except:
                url = '#'
            suggestions.append({
                'type': 'Menu',
                'text': item['text'],
                'url': url,
                'category': item['category']
            })

        # Students
        students = Students.objects.filter(
            Q(admin__first_name__icontains=query) |
            Q(admin__last_name__icontains=query) |
            Q(admin__username__icontains=query)
        ).select_related('admin', 'course_id')[:5]
        for student in students:
            suggestions.append({
                'type': 'Student',
                'text': f"{student.admin.first_name} {student.admin.last_name}",
                'url': reverse('student_detail_view', kwargs={'pk': student.id})
            })

        # Staff
        staff = Staffs.objects.filter(
            Q(admin__first_name__icontains=query) |
            Q(admin__last_name__icontains=query) |
            Q(admin__username__icontains=query)
        ).select_related('admin', 'role')[:5]
        for s in staff:
            suggestions.append({
                'type': 'Staff',
                'text': f"{s.admin.first_name} {s.admin.last_name}",
                'url': reverse('edit_staff', kwargs={'staff_id': s.admin.id})
            })

        # Subjects
        subjects = Subjects.objects.filter(subject_name__icontains=query)[:5]
        for subject in subjects:
            suggestions.append({
                'type': 'Subject',
                'text': subject.subject_name,
                'url': reverse('edit_subject', kwargs={'subject_id': subject.id})
            })

        # Courses
        courses = Courses.objects.filter(course_name__icontains=query)[:5]
        for course in courses:
            suggestions.append({
                'type': 'Class',
                'text': course.course_name,
                'url': reverse('edit_course', kwargs={'course_id': course.id})
            })

        # Books
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )[:5]
        for book in books:
            suggestions.append({
                'type': 'Book',
                'text': book.title,
                'url': '#'
            })

    return JsonResponse({'suggestions': suggestions})

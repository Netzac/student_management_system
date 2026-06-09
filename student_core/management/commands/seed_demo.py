"""Seed every project table with demo data so the system is demonstrable.

Idempotent: each table is topped up to at least ``--rows`` rows (default 3).
Re-running will not create duplicates of the lookup/unique rows and will only
add what is missing.  Run with::

    python manage.py seed_demo
    python manage.py seed_demo --rows 5

The order of operations matters because creating a ``CustomUser`` fires a
``post_save`` signal that auto-creates the matching ``Staffs``/``Students``
profile from the first Bank/Gender/Role/Courses/SessionYear rows, so those
lookup tables are seeded first.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from student_core.models import (
    Bank, Gender, Role, Courses, Subjects, SessionYearModel, AcademicTerm,
    CustomUser, Staffs, Students, ClassTeacher, Attendance, AttendanceReport,
    LeaveReportStudent, LeaveReportStaff, FeedBackStudent, FeedBackStaffs,
    NotificationStudent, NotificationStaffs, StudentResult, ConductInterestRemarks,
)
from student_account.models import (
    Earnings, Deductions, FeeType, Invoice, InvoiceItem, Receipt,
    TaxTable, Payroll, Staff_Deductions, Staff_Earnings,
)
from student_exam.models import (
    Exercise, Assignment, Submission, Gradebook, OverallGradebook,
)
from student_result.models import Result, ResultSummary, ClassExercise
from bookstore.models import (
    Category, SubCategory, Author, Book, Review, Slider, Stationery, RequiredItem,
)
from library.models import Borrow
from order.models import Order, OrderItem
from school.models import School
from sms.models import SMSLog

import os
from django.conf import settings

# Existing demo media files shipped in MEDIA_ROOT.  Report/result templates
# call ``.url`` on these FileFields, which raises ValueError when the field is
# empty, so we point the seeded rows at real files when they are present.
_SCHOOL_LOGO = "school/school_logo.jpg"
_SCHOOL_SEAL = "school/school_logo.jpg"
_SCHOOL_SIGN = "school/sign.jpg"
_STAFF_SIGN = "signature/sign.jpg"
_STUDENT_PIC = "student/default.jpg"


def _media(rel_path):
    """Return ``rel_path`` if the file exists under MEDIA_ROOT, else ``''``."""
    if rel_path and os.path.exists(os.path.join(settings.MEDIA_ROOT, rel_path)):
        return rel_path
    return ""


class Command(BaseCommand):
    help = "Seed all tables with at least N demo rows (default 3)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--rows", type=int, default=3,
            help="Minimum number of rows per table (default 3).",
        )

    def handle(self, *args, **options):
        self.n = max(3, options["rows"])
        with transaction.atomic():
            self._seed()
        self.stdout.write(self.style.SUCCESS(f"\nSeeding complete (target: {self.n} rows/table)."))

    # ------------------------------------------------------------------ helpers
    def _topup(self, source, target, factory, label=None):
        """Call ``factory(i)`` until ``source`` has ``target`` rows.

        ``source`` may be a model class or a queryset; counting works for both.
        """
        count = source.objects.count if hasattr(source, "objects") else source.count
        label = label or source.__name__
        existing = count()
        created = 0
        i = existing
        while count() < target:
            before = count()
            factory(i)
            i += 1
            if count() == before:
                # Factory made no progress (e.g. ran out of unique pairings).
                break
            created += 1
        self.stdout.write(f"  {label:<22} {count():>3} rows (+{created})")

    # ------------------------------------------------------------------ seeding
    def _seed(self):
        n = self.n
        today = date.today()

        # --- 1. Lookup tables (no FK dependencies) ---------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Lookup tables"))

        banks = ["Ghana Commercial Bank", "ABSA", "Ecobank", "Fidelity Bank", "CalBank"]
        self._topup(Bank, n, lambda i: Bank.objects.create(name=banks[i % len(banks)]))

        genders = ["Male", "Female", "Other", "Prefer not to say"]
        self._topup(Gender, n, lambda i: Gender.objects.create(gender_name=genders[i % len(genders)]))

        roles = [("Teacher", "Classroom teacher"), ("Administrator", "School admin"),
                 ("Accountant", "Finance officer"), ("Librarian", "Library staff"),
                 ("Counsellor", "Student counsellor")]
        self._topup(Role, n, lambda i: Role.objects.get_or_create(
            type=roles[i % len(roles)][0], defaults={"description": roles[i % len(roles)][1]}))

        classes = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"]
        self._topup(Courses, n, lambda i: Courses.objects.create(course_name=classes[i % len(classes)]))

        subjects = ["Mathematics", "English", "Science", "Social Studies", "ICT"]
        self._topup(Subjects, n, lambda i: Subjects.objects.create(subject_name=subjects[i % len(subjects)]))

        # NOTE: the result/report views extract the closing year via
        # ``str(session).split('to', 1)[1]`` (see student_result/views.py and
        # student_core/forms.py), so the session *name* MUST contain " to ".
        self._topup(SessionYearModel, n, lambda i: SessionYearModel.objects.get_or_create(
            name=f"{2020 + i} to {2021 + i}",
            defaults=dict(
                session_start_year=date(2020 + i, 9, 1),
                session_end_year=date(2021 + i, 7, 31),
                re_opening_date=date(2020 + i, 9, 15),
                current=(i == 0),
            )))

        terms = ["First Term", "Second Term", "Third Term", "Fourth Term"]
        self._topup(AcademicTerm, n, lambda i: AcademicTerm.objects.get_or_create(
            name=terms[i % len(terms)], defaults={"current": (i == 0)}))

        # --- 2. Users + profiles --------------------------------------------
        # Creating a CustomUser fires a post_save signal that *may* create the
        # matching AdminHOD/Staffs/Students profile.  But existing users can be
        # missing their profile (signal added later), and Staffs/Students.admin
        # is OneToOne, so we seed by *profile* count: each new profile gets a
        # brand-new user, guaranteeing >=n rows in AdminHOD, Staffs and Students.
        self.stdout.write(self.style.MIGRATE_HEADING("Users, staff & students"))

        from student_core.models import AdminHOD

        self._topup(AdminHOD, n,
                    lambda i: self._ensure_hod(i), label="AdminHOD")
        self._topup(Staffs, n,
                    lambda i: self._ensure_staff(i), label="Staffs")
        self._topup(Students, n,
                    lambda i: self._ensure_student(i), label="Students")

        self._enrich_staff()
        self._enrich_students()

        staff_list = list(Staffs.objects.all())
        student_list = list(Students.objects.all())
        course_list = list(Courses.objects.all())
        subject_list = list(Subjects.objects.all())
        session = SessionYearModel.objects.first()
        term = AcademicTerm.objects.first()

        # --- 3. ClassTeacher (OneToOne on BOTH staff and class) --------------
        # Each staff and each class may appear at most once, so pick only
        # combinations whose staff *and* class are still unassigned.
        self.stdout.write(self.style.MIGRATE_HEADING("Class teachers"))

        def make_class_teacher(i):
            used_staff = set(ClassTeacher.objects.values_list("staff_id_id", flat=True))
            used_cls = set(ClassTeacher.objects.values_list("cls_id_id", flat=True))
            free_staff = [s for s in staff_list if s.id not in used_staff]
            free_cls = [c for c in course_list if c.id not in used_cls]
            if not free_staff or not free_cls:
                return  # ran out of unique pairings; _topup will stop topping up
            ClassTeacher.objects.create(staff_id=free_staff[0], cls_id=free_cls[0])

        # Cap target at how many unique pairings are actually possible.
        ct_target = min(n, len(staff_list), len(course_list))
        self._topup(ClassTeacher, ct_target, make_class_teacher)

        # --- 4. Attendance ---------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Attendance"))
        self._topup(Attendance, n, lambda i: Attendance.objects.create(
            student_id=student_list[i % len(student_list)],
            course_id=course_list[i % len(course_list)],
            attendance_date=today - timedelta(days=i),
            session_year_id=session,
            status=bool(i % 2 == 0)))
        att_list = list(Attendance.objects.all())
        self._topup(AttendanceReport, n, lambda i: AttendanceReport.objects.create(
            student_id=student_list[i % len(student_list)],
            attendance_id=att_list[i % len(att_list)],
            status=bool(i % 2 == 0)))

        # --- 5. Leave / Feedback / Notifications -----------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Leave, feedback & notifications"))
        self._topup(LeaveReportStudent, n, lambda i: LeaveReportStudent.objects.create(
            student_id=student_list[i % len(student_list)],
            leave_date=str(today - timedelta(days=i)),
            leave_message=f"Demo student leave request #{i}", leave_status=i % 2))
        self._topup(LeaveReportStaff, n, lambda i: LeaveReportStaff.objects.create(
            staff_id=staff_list[i % len(staff_list)],
            leave_date=str(today - timedelta(days=i)),
            leave_message=f"Demo staff leave request #{i}", leave_status=i % 2))
        self._topup(FeedBackStudent, n, lambda i: FeedBackStudent.objects.create(
            student_id=student_list[i % len(student_list)],
            feedback=f"Demo student feedback #{i}", feedback_reply="Thank you for your feedback."))
        self._topup(FeedBackStaffs, n, lambda i: FeedBackStaffs.objects.create(
            staff_id=staff_list[i % len(staff_list)],
            feedback=f"Demo staff feedback #{i}", feedback_reply="Noted, thank you."))
        self._topup(NotificationStudent, n, lambda i: NotificationStudent.objects.create(
            student_id=student_list[i % len(student_list)],
            message=f"Demo student notification #{i}"))
        self._topup(NotificationStaffs, n, lambda i: NotificationStaffs.objects.create(
            stafff_id=staff_list[i % len(staff_list)],
            message=f"Demo staff notification #{i}"))

        # --- 6. Results & remarks (student_core) -----------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Core results & remarks"))
        self._topup(StudentResult, n, lambda i: StudentResult.objects.create(
            student_id=student_list[i % len(student_list)],
            subject_id=subject_list[i % len(subject_list)],
            subject_exam_marks=60 + i, subject_assignment_marks=20 + i))
        self._topup(ConductInterestRemarks, n, lambda i: ConductInterestRemarks.objects.create(
            student=student_list[i % len(student_list)],
            conduct="Excellent", interest="Football", remarks="Keep it up"))

        # --- 7. Exam app: gradebooks, exercises, assignments -----------------
        self.stdout.write(self.style.MIGRATE_HEADING("Exam app"))
        grades = [(70, "A", "Excellent"), (60, "B", "Very Good"), (50, "C", "Good"),
                  (40, "D", "Pass"), (0, "F", "Fail")]
        self._topup(Gradebook, n, lambda i: Gradebook.objects.create(
            lb=grades[i % len(grades)][0], grade=grades[i % len(grades)][1],
            remark=grades[i % len(grades)][2]))
        self._topup(OverallGradebook, n, lambda i: OverallGradebook.objects.create(
            lb=grades[i % len(grades)][0], grade=grades[i % len(grades)][1],
            remark=grades[i % len(grades)][2]))
        exercises = ["Quiz 1", "Quiz 2", "Homework 1", "Project 1", "Test 1"]
        self._topup(Exercise, n, lambda i: Exercise.objects.create(name=exercises[i % len(exercises)]))

        hod_user = CustomUser.objects.filter(user_type="1").first()
        self._topup(Assignment, n, lambda i: Assignment.objects.create(
            title=f"Demo Assignment {i}", content=f"Please complete demo assignment {i}.",
            due_date=today + timedelta(days=7 + i),
            course=course_list[i % len(course_list)],
            subject=subject_list[i % len(subject_list)], user=hod_user))
        assignment_list = list(Assignment.objects.all())
        student_users = list(CustomUser.objects.filter(user_type="3"))
        self._topup(Submission, n, lambda i: Submission.objects.create(
            matric_number=f"MAT-{1000 + i}", upload="submissions/demo.txt",
            answer=f"Demo answer for submission {i}",
            assignment=assignment_list[i % len(assignment_list)],
            user=student_users[i % len(student_users)],
            grade="A", feedback="Well done"))

        # --- 8. Result app ---------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Result app"))
        exercise_list = list(Exercise.objects.all())
        self._topup(Result, n, lambda i: Result.objects.create(
            student=student_list[i % len(student_list)], session=session, term=term,
            current_class=course_list[i % len(course_list)],
            subject=subject_list[i % len(subject_list)],
            test_score=20 + i, exam_score=50 + i))
        self._topup(ResultSummary, n, lambda i: ResultSummary.objects.create(
            student=student_list[i % len(student_list)], session=session, term=term,
            total=70 + i, grade="A", attendance=90 + i))
        self._topup(ClassExercise, n, lambda i: ClassExercise.objects.create(
            student=student_list[i % len(student_list)], session=session, term=term,
            current_class=course_list[i % len(course_list)],
            subject=subject_list[i % len(subject_list)],
            exercise=exercise_list[i % len(exercise_list)], score=60 + i))

        # --- 9. Accounts / payroll (student_account) -------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Accounts & payroll"))
        earn = [("Basic Salary", ""), ("Transport Allowance", ""), ("Bonus", ""),
                ("Overtime", ""), ("Housing Allowance", "")]
        self._topup(Earnings, n, lambda i: Earnings.objects.get_or_create(
            type=earn[i % len(earn)][0], defaults={"description": earn[i % len(earn)][1]}))
        ded = [("Tax", ""), ("Pension", ""), ("Loan Repayment", ""),
               ("Union Dues", ""), ("Insurance", "")]
        self._topup(Deductions, n, lambda i: Deductions.objects.get_or_create(
            type=ded[i % len(ded)][0], defaults={"description": ded[i % len(ded)][1]}))
        fees = [("Tuition", ""), ("Books", ""), ("Uniform", ""),
                ("Transport", ""), ("Exam Fee", "")]
        self._topup(FeeType, n, lambda i: FeeType.objects.get_or_create(
            type=fees[i % len(fees)][0], defaults={"description": fees[i % len(fees)][1]}))

        self._topup(TaxTable, n, lambda i: TaxTable.objects.create(
            chargeableIncome=Decimal(1000 * (i + 1)), rate=Decimal(5 * (i + 1))))

        feetype_list = list(FeeType.objects.all())
        self._topup(Invoice, n, lambda i: Invoice.objects.create(
            student=student_list[i % len(student_list)], session=session, term=term,
            class_for=course_list[i % len(course_list)],
            balance_from_previous_term=0, status="active"))
        invoice_list = list(Invoice.objects.all())
        self._topup(InvoiceItem, n, lambda i: InvoiceItem.objects.create(
            invoice=invoice_list[i % len(invoice_list)],
            feetype=feetype_list[i % len(feetype_list)], amount=500 * (i + 1)))
        self._topup(Receipt, n, lambda i: Receipt.objects.create(
            invoice=invoice_list[i % len(invoice_list)], amount_paid=300 * (i + 1),
            date_paid=today - timedelta(days=i), comment=f"Demo payment {i}"))

        self._topup(Payroll, n, lambda i: Payroll.objects.create(
            staff=staff_list[i % len(staff_list)],
            basic_pay=Decimal(2000 + 100 * i), period=f"2024-{(i % 12) + 1:02d}",
            earnings=Decimal(300), deductions=Decimal(150),
            payable_tax=Decimal(100), net_pay=Decimal(2050 + 100 * i)))
        payroll_list = list(Payroll.objects.all())
        earnings_list = list(Earnings.objects.all())
        deductions_list = list(Deductions.objects.all())
        self._topup(Staff_Earnings, n, lambda i: Staff_Earnings.objects.create(
            earnings=earnings_list[i % len(earnings_list)],
            staff=staff_list[i % len(staff_list)], amt=Decimal(200 + 10 * i),
            period=f"2024-{(i % 12) + 1:02d}", payroll=payroll_list[i % len(payroll_list)]))
        self._topup(Staff_Deductions, n, lambda i: Staff_Deductions.objects.create(
            deductions=deductions_list[i % len(deductions_list)],
            staff=staff_list[i % len(staff_list)], amt=Decimal(100 + 10 * i),
            period=f"2024-{(i % 12) + 1:02d}", payroll=payroll_list[i % len(payroll_list)]))

        # --- 10. Bookstore / library / orders --------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Bookstore, library & orders"))
        cats = ["Textbooks", "Novels", "Reference", "Children", "Science"]
        self._topup(Category, n, lambda i: Category.objects.create(
            name=cats[i % len(cats)], description=f"{cats[i % len(cats)]} category"))
        category_list = list(Category.objects.all())
        self._topup(SubCategory, n, lambda i: SubCategory.objects.create(
            category=category_list[i % len(category_list)],
            name=f"Sub {cats[i % len(cats)]} {i}", description="Demo sub category"))
        authors = ["Chinua Achebe", "Ama Ata Aidoo", "Ngugi wa Thiong'o",
                   "Wole Soyinka", "Buchi Emecheta"]
        self._topup(Author, n, lambda i: Author.objects.create(
            name=authors[i % len(authors)],
            slug=slugify(f"{authors[i % len(authors)]}-{i}"),
            bio=f"Biography of {authors[i % len(authors)]}"))
        self._topup(Book, n, lambda i: Book.objects.create(
            category=category_list[i % len(category_list)], isbn=f"978-000-{1000 + i}",
            title=f"Demo Book {i}", description="A demonstrable book.",
            author=authors[i % len(authors)], publisher="Demo Publishers",
            date_published=timezone.now(), price=50 + i, stock=100 - i))
        book_list = list(Book.objects.all())
        review_users = list(CustomUser.objects.all())
        self._topup(Review, n, lambda i: Review.objects.create(
            customer=review_users[i % len(review_users)],
            book=book_list[i % len(book_list)],
            review_star=(i % 5) + 1, review_text=f"Demo review {i}"))
        self._topup(Slider, n, lambda i: Slider.objects.create(
            title=f"Demo Slide {i}", slideimg="slide/demo.jpg"))
        items = ["Pen", "Pencil", "Notebook", "Eraser", "Ruler"]
        self._topup(Stationery, n, lambda i: Stationery.objects.create(
            item=items[i % len(items)], desc=f"{items[i % len(items)]} for class use"))
        stationery_list = list(Stationery.objects.all())
        self._topup(RequiredItem, n, lambda i: RequiredItem.objects.create(
            item=stationery_list[i % len(stationery_list)], qty=(i % 5) + 1,
            cls=course_list[i % len(course_list)]))

        self._topup(Borrow, n, lambda i: Borrow.objects.create(
            student=student_list[i % len(student_list)], book=book_list[i % len(book_list)],
            borrowing_date=today - timedelta(days=i),
            return_date=today + timedelta(days=14 - i), status=str((i % 2) + 1)))

        self._topup(Order, n, lambda i: Order.objects.create(
            customer=review_users[i % len(review_users)], name=f"Demo Customer {i}",
            email=f"customer{i}@demo.test", phone=f"02000000{i:02d}",
            address=f"{i} Demo Street", division="Greater Accra", zip_code="00233",
            payment_method="Cash", payable=100 * (i + 1), totalbook=(i % 3) + 1, paid=bool(i % 2)))
        order_list = list(Order.objects.all())
        self._topup(OrderItem, n, lambda i: OrderItem.objects.create(
            order=order_list[i % len(order_list)], book=book_list[i % len(book_list)],
            price=Decimal(50 + i), quantity=(i % 3) + 1))

        # --- 11. School & SMS ------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("School & SMS"))
        hod_users = list(CustomUser.objects.filter(user_type="1"))
        bank_list = list(Bank.objects.all())
        # School.admin is OneToOne -> one school per distinct admin user
        def make_school(i):
            admin = hod_users[i % len(hod_users)]
            if School.objects.filter(admin=admin).exists():
                # fall back to any HOD user without a school
                free = [u for u in hod_users if not School.objects.filter(admin=u).exists()]
                if not free:
                    return
                admin = free[0]
            School.objects.create(
                name=f"Demo Academy {i}", motto="Knowledge is Power",
                phone=f"030200000{i}", email=f"school{i}@demo.test",
                address=f"{i} Education Road", branch=f"Branch {i}",
                bank=bank_list[i % len(bank_list)], admin=admin,
                logo=_media(_SCHOOL_LOGO), seal=_media(_SCHOOL_SEAL),
                adminSignature=_media(_SCHOOL_SIGN))
        self._topup(School, min(n, len(hod_users)), make_school)

        # Back-fill empty file fields on any existing schools so report
        # templates that call ``logo.url`` / ``seal.url`` do not raise.
        for school in School.objects.all():
            changed = False
            if not str(school.logo) and _media(_SCHOOL_LOGO):
                school.logo = _media(_SCHOOL_LOGO); changed = True
            if not str(school.seal) and _media(_SCHOOL_SEAL):
                school.seal = _media(_SCHOOL_SEAL); changed = True
            if not str(school.adminSignature) and _media(_SCHOOL_SIGN):
                school.adminSignature = _media(_SCHOOL_SIGN); changed = True
            if changed:
                school.save()

        sms_status = ["sent", "failed", "skipped"]
        sms_trigger = ["fee_payment", "bulk_sms", "manual"]
        self._topup(SMSLog, n, lambda i: SMSLog.objects.create(
            recipient_phone=f"02011111{i:02d}", recipient_name=f"Recipient {i}",
            message=f"Demo SMS message {i}", status=sms_status[i % len(sms_status)],
            trigger=sms_trigger[i % len(sms_trigger)],
            sent_by=hod_users[i % len(hod_users)] if hod_users else None))

    # ------------------------------------------------------------------ users
    def _make_user(self, prefix, user_type, first, last):
        """Create a fresh CustomUser; the post_save signal builds its profile."""
        i = CustomUser.objects.count()
        username = f"{prefix}{i}"
        while CustomUser.objects.filter(username=username).exists():
            i += 1
            username = f"{prefix}{i}"
        user = CustomUser.objects.create(
            username=username, first_name=first, last_name=f"{last}{i}",
            email=f"{username}@demo.test", user_type=user_type)
        user.set_password("demo12345")
        user.save()
        return user

    def _ensure_hod(self, i):
        from student_core.models import AdminHOD
        user = self._make_user("hod", 1, "Helen", "HOD")
        # Signal creates AdminHOD for user_type==1; create defensively if not.
        AdminHOD.objects.get_or_create(admin=user)

    def _ensure_staff(self, i):
        user = self._make_user("staff", 2, "Sam", "Staff")
        if not Staffs.objects.filter(admin=user).exists():
            Staffs.objects.create(
                admin=user, bank=Bank.objects.first(),
                gender=Gender.objects.first(), role=Role.objects.first(),
                address="")

    def _ensure_student(self, i):
        user = self._make_user("student", 3, "Stella", "Student")
        if not Students.objects.filter(admin=user).exists():
            Students.objects.create(
                admin=user, course_id=Courses.objects.first(),
                session_year_id=SessionYearModel.objects.first(),
                gender=Gender.objects.first(), address="",
                parent_first_name="Parent", parent_last_name="Guardian")

    def _enrich_staff(self):
        """Fill in required-but-default fields on signal-created Staffs rows."""
        gender = Gender.objects.first()
        role = Role.objects.first()
        bank = Bank.objects.first()
        for idx, staff in enumerate(Staffs.objects.all()):
            changed = False
            if not staff.address:
                staff.address = f"{idx} Staff Quarters, Demo City"
                changed = True
            if not staff.contact_number:
                staff.contact_number = f"02055555{idx:02d}"
                changed = True
            if staff.gender_id is None:
                staff.gender = gender; changed = True
            if staff.role_id is None:
                staff.role = role; changed = True
            if staff.bank_id is None:
                staff.bank = bank; changed = True
            if not staff.ss_no:
                staff.ss_no = f"SSN{1000 + idx}"; changed = True
            if not staff.bank_acc_no:
                staff.bank_acc_no = f"ACC{10000 + idx}"; changed = True
            if not staff.signature and _media(_STAFF_SIGN):
                staff.signature = _media(_STAFF_SIGN); changed = True
            if changed:
                staff.save()

    def _enrich_students(self):
        """Fill in required fields on signal-created Students rows."""
        gender = Gender.objects.first()
        course = Courses.objects.first()
        session = SessionYearModel.objects.first()
        for idx, student in enumerate(Students.objects.all()):
            changed = False
            if not student.address:
                student.address = f"{idx} Student Lane, Demo City"; changed = True
            if not str(student.profile_pic) and _media(_STUDENT_PIC):
                student.profile_pic = _media(_STUDENT_PIC); changed = True
            if student.gender_id is None:
                student.gender = gender; changed = True
            if student.course_id_id is None:
                student.course_id = course; changed = True
            if student.session_year_id_id is None:
                student.session_year_id = session; changed = True
            if not student.parent_first_name:
                student.parent_first_name = "Parent"; changed = True
            if not student.parent_last_name:
                student.parent_last_name = f"Guardian{idx}"; changed = True
            if not student.parent_contact_number:
                student.parent_contact_number = f"02066666{idx:02d}"; changed = True
            if not student.parent_occupation:
                student.parent_occupation = "Trader"; changed = True
            if changed:
                student.save()

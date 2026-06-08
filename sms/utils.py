from student_core.models import Courses, Students


def _guardian_name(student):
    return f"{student.parent_first_name} {student.parent_last_name}".strip()


def _student_to_recipient(student):
    phone = (student.parent_contact_number or "").strip()
    if not phone:
        return None
    return {"phone": phone, "name": _guardian_name(student)}


def build_all_guardian_recipients():
    recipients = []
    seen_phones = set()
    students = Students.objects.filter(
        status="1",
        delete_flag=0,
    ).exclude(parent_contact_number__isnull=True).exclude(parent_contact_number="")

    for student in students:
        recipient = _student_to_recipient(student)
        if recipient and recipient["phone"] not in seen_phones:
            seen_phones.add(recipient["phone"])
            recipients.append(recipient)
    return recipients


def build_class_recipients(class_id):
    if not class_id:
        return []

    recipients = []
    seen_phones = set()
    students = Students.objects.filter(
        course_id_id=class_id,
        status="1",
        delete_flag=0,
    ).exclude(parent_contact_number__isnull=True).exclude(parent_contact_number="")

    for student in students:
        recipient = _student_to_recipient(student)
        if recipient and recipient["phone"] not in seen_phones:
            seen_phones.add(recipient["phone"])
            recipients.append(recipient)
    return recipients


def build_individual_recipients(student_id_list):
    if not student_id_list:
        return []

    recipients = []
    students = Students.objects.filter(
        pk__in=student_id_list,
        status="1",
        delete_flag=0,
    )

    for student in students:
        recipient = _student_to_recipient(student)
        if recipient:
            recipients.append(recipient)
    return recipients


def get_class_choices():
    return Courses.objects.all().order_by("course_name")

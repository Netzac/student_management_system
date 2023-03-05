def get_teacher_cls_id(request):
    return request.user.staffs.classteacher.cls_id.id

def get_student_cls_id(request):
    return request.user.students.course_id.id
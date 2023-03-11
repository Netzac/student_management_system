from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO

from student_exam.models import Gradebook, OverallGradebook
from  student_core.models import AcademicTerm as Term, Courses as Class

def score_grade2(score):
    if score >= 70:
        return "A"
    elif score >=60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >=40:
        return "D"
    elif score>=30:
        return "E"
    else:
        return "F"


def score_grade(score):

    gradescale = Gradebook.objects.values_list('lb','grade','remark').order_by('-lb')
    for (lb, grade,remark) in gradescale:

        if score >= lb:
            return (grade,remark,)
            break
        else:
            continue
    
def score_overall_grade(score):

    gradescale = OverallGradebook.objects.values_list('lb','grade').order_by('-lb')
    for (lb, grade) in gradescale:

        if score >= lb:
            return (grade)
            break
        else:
            continue
       

def renderPdf(template, content={}):
    t = get_template(template)
    send_data = t.render(content)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(send_data.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        return None
    

def get_teacher_cls_id(request):
    return request.user.staffs.classteacher.cls_id.id

def get_student_cls_id(request):
    return request.user.students.course_id.id


def is_last_term(term):
    last_term = Term.objects.order_by('id').last().name
    print('is_last',last_term)
    return str(last_term) == str(term)
    
def get_next_class(cls_id):
    next_cls = None
    try:
        next_cls = Class.objects.filter(id__gt = cls_id).order_by('id').first()
    except:
        pass 
    
    if next_cls:
        return next_cls.course_name
    else:
        return "N/A"
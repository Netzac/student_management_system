from requests import session
from student_account.models import Invoice

from django.apps import apps
from student_core.models import  SessionYearModel
from student_account.models import Invoice

def get_prev_term_id(id):
    #tbl_obj= apps.get_model('student_account',str(tbl))
    try:
        prev_id = SessionYearModel.objects.values('id').filter(id__lt = id).order_by('-id').first()
        return prev_id['id']
    except:
        return None

def get_prev_term_bills(id):
    try:
        prev_id = get_prev_term_id(id)
        return Invoice.objects.filter(session=prev_id)
    except:
        return None
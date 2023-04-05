from .models import SessionYearModel as AcademicSession, AcademicTerm


class SiteWideConfigs:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            (cur_session_obj, created) = AcademicSession.objects.get_or_create(current=True)
            (cur_term_obj, created) = AcademicTerm.objects.get_or_create(current=True)

            current_session = cur_session_obj##AcademicSession.objects.get(current=True)
            current_term = cur_term_obj ##AcademicTerm.objects.get(current=True)
            current_session_id= current_session.id

        except AcademicSession.DoesNotExist and AcademicTerm.DoesNotExist:
            current_session = None
            current_term = None
            current_session_id= None



        request.current_session = current_session
        request.current_term = current_term
        request.current_session_id = current_session_id

        response = self.get_response(request)

        return response

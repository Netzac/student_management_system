from .models import SessionYearModel as AcademicSession, AcademicTerm


class SiteWideConfigs:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            current_session = AcademicSession.objects.get(current=True)
            current_term = AcademicTerm.objects.get(current=True)
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

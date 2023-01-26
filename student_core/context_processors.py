from .models import SessionYearModel as AcademicSession, AcademicTerm #, SiteConfig


def site_defaults(request):

    try:
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.get(current=True)
        session_id = current_session.id
        #vals = SiteConfig.objects.all()
        contexts = {
            "current_session": current_session.name,
            "current_term": current_term.name,
            "session_id": session_id,
        }
    except AcademicSession.DoesNotExist and AcademicTerm.DoesNotExist:
        contexts = {
            "current_session": None,
            "current_term": None,
            "session_id":None,
        }
    # for val in vals:
    #     contexts[val.key] = val.value

    return contexts

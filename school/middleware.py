from django.shortcuts import redirect
from django.urls import reverse
from school.models import School

class SchoolSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if school exists
            if not School.objects.exists():
                # Define urls that should be accessible even without school
                allowed_urls = [
                    reverse('school-create'),
                    reverse('logout_user'),
                    reverse('password_reset'),
                ]
                # Check if request path is in allowed urls
                if request.path not in allowed_urls and not request.path.startswith('/admin/'):
                    return redirect('school-create')
        response = self.get_response(request)
        return response

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from student_management_system import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('student_core.urls')),
    path('studentaccount/', include('student_account.urls')),
    path('result/', include('student_result.urls')),
    path('exam/', include('student_exam.urls')),
    path('lib/', include('library.urls')),
    path('bookstore/', include('bookstore.urls')),
    path('search/', include('search.urls')),
    path('order/', include('order.urls')),
    path('cart/', include('cart.urls')),
    path('school/', include('school.urls')),
    
   
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



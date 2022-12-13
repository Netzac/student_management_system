from imp import load_dynamic
from django.urls import path,re_path

from .views import (
    ResultListView,ResultDetailView, create_result,
     edit_results,find_result, 
     load_students,select_result_class,
)

urlpatterns = [
    path("create/<clsid>", create_result, name="create-result"),
    path("edit-results/<clsid>", edit_results, name="edit-results"),
    # re_path(r'^edit-results/(?P<student>\d+,*\d*)', edit_results, name="edit-results"),
    path('get-result/<student>',ResultDetailView, name='get-result'),
    path('find-result/',find_result, name='find-result'),
    path('select-result-class/',select_result_class, name='select-result-class'),
    path("view/all", ResultListView.as_view(), name="view-results"),

    path("ajax/load-students",load_students , name="load-students"),
]

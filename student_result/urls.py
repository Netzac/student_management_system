from imp import load_dynamic
from django.urls import path,re_path

from .views import (
    ResultListView,ResultDetailView,ClassResultDetailView, create_result,
     edit_results,find_result, 
     load_students,select_result_class,pdf,select_ex_class,create_ex_result
)

urlpatterns = [
    path("create/<clsid>", create_result, name="create-result"),
    path("edit-results/<clsid>/<students>", edit_results, name="edit-results"),
    # re_path(r'^edit-results/(?P<student>\d+,*\d*)', edit_results, name="edit-results"),
    path('get-result/<student>',ResultDetailView, name='get-result'),
    path('get-class-result/<clsid>/All/',ClassResultDetailView, name='get-class-result'),
    path('find-result/',find_result, name='find-result'),
    path('select-result-class/',select_result_class, name='select-result-class'),
    path("view/all", ResultListView.as_view(), name="view-results"),

    path('select-exercise-class/',select_ex_class, name='ex-result-class'),
    path("create/<clsid>/ex/", create_ex_result, name="create-ex-result"),
    #path("edit-results/<clsid>/<students>", edit_results, name="edit-results"),

    path("ajax/load-students",load_students , name="load-students"),
path('pdf/', pdf.as_view(), name='results-pdf'),
]

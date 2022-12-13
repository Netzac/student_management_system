
from django.urls import path

from student_exam.views import (
    create_assignment, dashboard,assignment_submissions,
    assignment_detail,delete_assignment, edit_submission,
     edit_assignment, delete_submission, edit_submission, submit_assignment
)

urlpatterns = [
    path('assignments/',create_assignment, name="create-assignment"),
    path('dashboard/', dashboard, name="dashboard"),
    path('assignments/<id>/submissions',assignment_submissions, name='submissions'),
    path('assignments/<id>/detail/',assignment_detail,name='assignment-detail'),
    path('assignments/<id>/delete/',delete_assignment,name='delete-assignment'),
    path('assignments/<id>/submission',submit_assignment,name='assignment-submission'),
    path('submissions/<id>/edit/',edit_submission, name='edit-submission'),
    path('assignments/<id>/edit/', edit_assignment,name='edit-assignment'),
    path('submissions/<id>/delete',delete_submission,name='delete-submission'),
    path('submissions/<id>/detail',edit_submission,name='submission-detail'),
    
]

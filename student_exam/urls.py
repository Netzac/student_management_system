
from django.urls import path

from student_exam.views import (
    create_assignment, dashboard,assignment_submissions,
    assignment_detail,delete_assignment, edit_submission,
     edit_assignment, delete_submission, edit_submission, submit_assignment,
     gradebook,manage_gradebook,save_gradebook,delete_gradebook,view_gradebook,
     overall_gradebook,manage_overall_gradebook,delete_overall_gradebook,save_overall_gradebook,
     view_overall_gradebook,
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


    path('books',gradebook,name='gradebook'),
    path('manage_book',manage_gradebook,name='manage-gradebook'),
    path('manage_book/<int:pk>',manage_gradebook,name='manage-gradebook-pk'),
    path('view_book/<int:pk>',view_gradebook,name='view-gradebook-pk'),
    path('save_book',save_gradebook,name='save-gradebook'),
    path('delete_book/<int:pk>',delete_gradebook,name='delete-gradebook'),


    path('overall_gradebook',overall_gradebook,name='overall-gradebook'),
    path('manage_overall_gradebook',manage_overall_gradebook,name='manage-overall-gradebook'),
    path('manage_overall_gradebook/<int:pk>',manage_overall_gradebook,name='manage-overall-gradebook-pk'),
    path('view_overall_gradebook/<int:pk>',view_overall_gradebook,name='view-overall-gradebook-pk'),
    path('save_overall_gradebook',save_overall_gradebook,name='save-overall-gradebook'),
    path('delete_overall_gradebook/<int:pk>',delete_overall_gradebook,name='delete-overall-gradebook'),
    
]

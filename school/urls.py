from django.urls import path
from . import views



urlpatterns = [
	path('detail/<int:pk>', views.SchoolDetailView.as_view(), name='school-details'),
	path('', views.SchoolListView.as_view(), name='school-list'),
    path('create/', views.SchoolCreateView.as_view(), name='school-create'),
	path('update/<int:pk>', views.SchoolUpdateView.as_view(), name='school-update'),
    path('delete/<int:pk>', views.SchoolDeleteView.as_view(), name='school-delete'),
]

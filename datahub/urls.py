from django.urls import path
from . import views

app_name = 'datahub'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('entity/<slug:entity_slug>/', views.entity_detail, name='entity_detail'),
    
    # Import flows
    path('entity/<slug:entity_slug>/import/', views.import_start, name='import_start'),
    path('entity/<slug:entity_slug>/template/', views.import_template, name='import_template'),
    path('import/status/<int:job_id>/', views.import_status, name='import_status'),
    
    # Export flows
    path('entity/<slug:entity_slug>/export/', views.export_start, name='export_start'),
    path('export/status/<int:job_id>/', views.export_status, name='export_status'),
    path('export/download/<int:job_id>/', views.export_download, name='export_download'),
]

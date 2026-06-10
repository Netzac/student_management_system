from django.contrib import admin
from .models import DataProject, ImportJob, ExportJob, JobLog


@admin.register(DataProject)
class DataProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name']


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ['entity_display', 'status', 'total_rows',
                   'imported_rows', 'error_rows', 'imported_by', 'started_at']
    list_filter = ['status', 'entity_slug', 'file_format']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ['entity_display', 'status', 'record_count',
                   'file_format', 'exported_by', 'started_at']
    list_filter = ['status', 'entity_slug']


@admin.register(JobLog)
class JobLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message', 'row_number', 'created_at']
    list_filter = ['level']

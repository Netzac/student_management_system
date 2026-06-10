from django.db import models
from django.conf import settings


class DataProject(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='data_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class ImportJob(models.Model):
    STATUS_CHOICES = [
        ('Queued', 'Queued'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('CompletedWithErrors', 'Completed with Errors'),
        ('Failed', 'Failed'),
    ]

    project = models.ForeignKey(DataProject, on_delete=models.CASCADE,
                               related_name='import_jobs', null=True, blank=True)
    entity_slug = models.CharField(max_length=100)
    entity_display = models.CharField(max_length=200)
    file_name = models.CharField(max_length=300)
    file_format = models.CharField(max_length=10,
                                  choices=[('xlsx', 'Excel'), ('csv', 'CSV')])
    status = models.CharField(max_length=30,
                           choices=STATUS_CHOICES, default='Queued')
    total_rows = models.IntegerField(default=0)
    imported_rows = models.IntegerField(default=0)
    skipped_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)
    duplicate_rows = models.IntegerField(default=0)
    on_duplicate = models.CharField(max_length=10,
                                   choices=[('skip', 'Skip'), ('overwrite', 'Overwrite')],
                                   default='skip')
    imported_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      on_delete=models.SET_NULL, null=True, related_name='import_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_file = models.FileField(upload_to='datahub/errors/', null=True, blank=True)

    def __str__(self):
        return f'{self.entity_display} [{self.status}]'

    class Meta:
        ordering = ['-created_at']


class ExportJob(models.Model):
    STATUS_CHOICES = ImportJob.STATUS_CHOICES

    project = models.ForeignKey(DataProject, on_delete=models.CASCADE,
                               related_name='export_jobs', null=True, blank=True)
    entity_slug = models.CharField(max_length=100)
    entity_display = models.CharField(max_length=200)
    file_format = models.CharField(max_length=10,
                                  choices=[('xlsx', 'Excel'), ('csv', 'CSV')])
    status = models.CharField(max_length=30,
                           choices=STATUS_CHOICES, default='Queued')
    record_count = models.IntegerField(default=0)
    filters_applied = models.JSONField(default=dict)
    exported_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL, null=True, related_name='export_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    output_file = models.FileField(upload_to='datahub/exports/', null=True, blank=True)

    def __str__(self):
        return f'{self.entity_display} [{self.status}]'

    class Meta:
        ordering = ['-created_at']


class JobLog(models.Model):
    LEVEL_CHOICES = [('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error')]

    import_job = models.ForeignKey(ImportJob, on_delete=models.CASCADE,
                                  related_name='logs', null=True, blank=True)
    export_job = models.ForeignKey(ExportJob, on_delete=models.CASCADE,
                                  related_name='logs', null=True, blank=True)
    row_number = models.IntegerField(null=True, blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    raw_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

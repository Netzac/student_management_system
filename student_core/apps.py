from django.apps import AppConfig


class StudentCoreConfig(AppConfig):
    name = 'student_core'

    def ready(self):
        from . import signals

from django.apps import AppConfig


class StudentAccountConfig(AppConfig):
    name = 'student_account'

    def ready(self):
        import student_account.signals  # noqa: F401

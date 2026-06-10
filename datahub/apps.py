from django.apps import AppConfig


class DatahubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datahub'
    verbose_name = 'Data Hub'

    def ready(self):
        try:
            from datahub import entity_registry
        except ImportError:
            pass

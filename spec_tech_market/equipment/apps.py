import sys
from django.apps import AppConfig

class EquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipment'

    def ready(self):
        import equipment.signals

        if 'runserver' in sys.argv or 'runworker' in sys.argv:
            from .scheduler import start_scheduler
            start_scheduler()


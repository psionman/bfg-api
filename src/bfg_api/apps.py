# bfg_api/apps.py
from django.apps import AppConfig

class BfgApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bfg_api"

    def ready(self):
        from .logging_setup import configure_structlog
        configure_structlog()

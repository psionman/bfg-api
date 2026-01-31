# bfg_api/apps.py
from django.apps import AppConfig
from .logging_setup import configure_structlog

class BfgApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bfg_api"

    def ready(self):
        configure_structlog()

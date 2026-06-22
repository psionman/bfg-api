# config/settings.py
"""
Django settings for bfg-api project.
"""

from pathlib import Path

from dotenv import load_dotenv

from .cors import (
    bfg_cors_allowed_origins,
    cors_allow_headers,
    cors_allow_methods,
    cors_allowed_origin_regexes,
    cors_allowed_origins,
)
from .csrf import (
    csrf_cookie_samesite,
    csrf_cookie_secure,
    csrf_trusted_origins,
    session_cookie_secure,
)
from .definitions import (
    get_allowed_hosts,
    get_auth_password_validators,
    get_databases,
    get_installed_apps,
    get_middleware,
    get_templates,
)
from .environ import (
    active_log_modules,
    app_log_to_console,
    get_debug_state,
    set_secret_key,
    set_thread_env_vars,
)
from .logging import setup_logging

load_dotenv()

set_thread_env_vars()
SECRET_KEY = set_secret_key()
DEBUG = get_debug_state()

# Setup logging
LOGGING = setup_logging(active_log_modules(), app_log_to_console(DEBUG))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEV_PORTS = ["5173", "5174", "5175", "8888", "8000"]

# CSRF
CSRF_TRUSTED_ORIGINS = csrf_trusted_origins(debug=DEBUG, dev_ports=DEV_PORTS)
CSRF_COOKIE_SAMESITE = csrf_cookie_samesite(DEBUG)
CSRF_COOKIE_SECURE = csrf_cookie_secure(DEBUG)
SESSION_COOKIE_SECURE = session_cookie_secure(DEBUG)

# CORS
BFG_CORS_ALLOWED_ORIGINS = bfg_cors_allowed_origins()
CORS_ALLOWED_ORIGINS = cors_allowed_origins(debug=DEBUG, dev_ports=DEV_PORTS)
CORS_ALLOWED_ORIGIN_REGEXES = cors_allowed_origin_regexes()
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = cors_allow_methods()
CORS_ALLOW_HEADERS = cors_allow_headers()


# Application definition
ALLOWED_HOSTS = get_allowed_hosts()

INSTALLED_APPS = get_installed_apps()

MIDDLEWARE = get_middleware()

ROOT_URLCONF = "config.urls"

TEMPLATES = get_templates(BASE_DIR)

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = get_databases(BASE_DIR)

AUTH_PASSWORD_VALIDATORS = get_auth_password_validators()


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

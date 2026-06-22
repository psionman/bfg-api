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
LOGGING = setup_logging(app_log_to_console(DEBUG), active_log_modules())

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhostwww.bidforgame.com",
    "bidforgame.com",
    "bidforgame.co.uk",
    "www.bidforgame.co.uk",  # ← add this if you use www on .co.uk too
    ".bidforgame.com",  # ← wildcard for all subdomains
    ".bidforgame.co.uk",
]
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEV_PORTS = ["5173", "5174", "5175", "8888", "8000"]

CSRF_TRUSTED_ORIGINS = csrf_trusted_origins(debug=DEBUG, dev_ports=DEV_PORTS)
CSRF_COOKIE_SAMESITE = csrf_cookie_samesite(DEBUG)
CSRF_COOKIE_SECURE = csrf_cookie_secure(DEBUG)
SESSION_COOKIE_SECURE = session_cookie_secure(DEBUG)

BFG_CORS_ALLOWED_ORIGINS = bfg_cors_allowed_origins()
CORS_ALLOWED_ORIGINS = cors_allowed_origins(debug=DEBUG, dev_ports=DEV_PORTS)
CORS_ALLOWED_ORIGIN_REGEXES = cors_allowed_origin_regexes()
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = cors_allow_methods()
CORS_ALLOW_HEADERS = cors_allow_headers()


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # Local
    "pages",
    "common",
    "rest_framework",
    "bfg_api.apps.BfgApiConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be as high as possible
    "common.middleware.cors.BfgCorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR.joinpath("templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


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

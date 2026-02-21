"""
Django settings for bfg-api project.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path
import logging
import structlog
from dotenv import load_dotenv


load_dotenv()

os.environ["OMP_NUM_THREADS"] = "1"        # OpenMP / BLAS threads
os.environ["MKL_NUM_THREADS"] = "1"        # Intel MKL
os.environ["OPENBLAS_NUM_THREADS"] = "1"   # OpenBLAS
os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # Apple vecLib
os.environ["NUMEXPR_NUM_THREADS"] = "1"    # numexpr

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is not set")

DEBUG = False if os.getenv('DEBUG', 'False') == 'False' else True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/


ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost'
    'www.bidforgame.com',
    'bidforgame.com',
    'bidforgame.co.uk',
    'www.bidforgame.co.uk',          # ← add this if you use www on .co.uk too
    '.bidforgame.com',               # ← wildcard for all subdomains
    '.bidforgame.co.uk',
]
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8888',          # ← your frontend/dev server
    'http://127.0.0.1:8888',          # sometimes browsers send this

    # Production ones – include scheme!
    'https://www.bidforgame.com',
    'https://bidforgame.com',
    'https://bidforgame.co.uk',
    "https://bidforgame.netlify.app",
    "https://*.netlify.app",
    # If you have subdomains or variants later: 'https://*.bidforgame.com'
]

BFG_CORS_ALLOWED_ORIGINS = [
    "https://bidforgame.netlify.app",
]

# dev convenience
if DEBUG:
    BFG_CORS_ALLOWED_ORIGINS += [
        "http://localhost:8888",
        "http://127.0.0.1:8888",
        "http://localhost:5173",  # vite
    ]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8888",     # your frontend port
    "http://127.0.0.1:8888",
#     # Add production:
    "https://www.bidforgame.com",
    "https://bidforgame.com",
    "https://bidforgame.co.uk",
    "https://www.bidforgame.co.uk",
    "https://bidforgame.netlify.app",
    # "https://*.netlify.app",           # optional but convenient for previews
]


CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.netlify\.app$",
]

# Explicitly allow OPTIONS
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True  # Required for cookies to be sent/received

if DEBUG:
    CSRF_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
else:
    CSRF_COOKIE_SAMESITE = "None"  # Not sure about this in production
    CSRF_COOKIE_SECURE = True  # True only in HTTPS


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',

    # Local
    'pages',
    'common',
    'rest_framework',
    'bfg_api.apps.BfgApiConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be as high as possible
    "common.middleware.cors.BfgCorsMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'structlog_json': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
            'foreign_pre_chain': [
                structlog.processors.TimeStamper(fmt='iso', utc=True),
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
            ],
        },
    },

    'handlers': {
        'file_json': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/bfg.log',
            'maxBytes': 5_000_000,
            'backupCount': 10,
            'formatter': 'structlog_json',
            'level': 'INFO',
            # 'level': 'WARNING',   # or 'WARNING' if you want quieter
        },
    },
    'loggers': {
        '': {
            'handlers': ['file_json'],
            # 'level': 'INFO',   # or 'WARNING' if you want quieter
            'level': 'WARNING',   # or 'WARNING' if you want quieter
            'propagate': False,
        },
        'django': {
            'handlers': ['file_json'],
            'level': 'WARNING',
            'propagate': False,
        },

        'django.server': {
            'handlers': ['file_json'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

if DEBUG:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logging.getLogger().addHandler(console)
    print("Forced console handler for DEBUG mode")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

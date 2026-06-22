# config/definitions.py
from pathlib import Path


def get_allowed_hosts():
    return [
        "127.0.0.1",
        "localhostwww.bidforgame.com",
        "bidforgame.com",
        "bidforgame.co.uk",
        "www.bidforgame.co.uk",  # ← add this if you use www on .co.uk too
        ".bidforgame.com",  # ← wildcard for all subdomains
        ".bidforgame.co.uk",
    ]


def get_installed_apps():
    return [
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


def get_middleware():
    return [
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


def get_templates(base_dir: str):
    return [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(Path(base_dir).joinpath("templates"))],
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


def get_databases(base_dir: str):
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(base_dir) / "db.sqlite3",
        }
    }


def get_auth_password_validators():
    return [
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

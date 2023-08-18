"""
Django settings for the project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from glob import glob
from pathlib import Path

import dj_database_url
import sentry_sdk
from corsheaders.defaults import default_headers
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

production = os.getenv("DJANGO_ENV") == "production"
local_access = "LOCAL_ACCESS" in os.environ or "ALLOWED_HOSTS" not in os.environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "i#y833-1r1g^fiq63y_5+v+zmc%ax_6g8$^^o&x%f2bo3omgif")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not production

ALLOWED_HOSTS = [".localhost", "127.0.0.1", "[::1]", "0.0.0.0"]
if "ALLOWED_HOSTS" in os.environ:
    ALLOWED_HOSTS.extend(os.getenv("ALLOWED_HOSTS").split(","))


# Application definition

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_celery_beat",
    "django_celery_results",
    "corsheaders",
    "core",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_transfer.TransferMiddleware",
]

ROOT_URLCONF = "spoonbill_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "spoonbill_web.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(default="postgresql:///spoonbill_web?application_name=spoonbill_web")}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Routes

API_PREFIX = os.getenv("API_PREFIX", "api/")
APPEND_SLASH = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Project-specific Django configuration

LOCALE_PATHS = glob(str(BASE_DIR / "**" / "locale"))

STATIC_ROOT = BASE_DIR / "static"

# https://docs.djangoproject.com/en/4.2/topics/logging/#django-security
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "backoff": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
if production and not local_access:
    # Run: env DJANGO_ENV=production SECURE_HSTS_SECONDS=1 ./manage.py check --deploy
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_REFERRER_POLICY = "same-origin"  # default in Django >= 3.1

    # https://docs.djangoproject.com/en/4.2/ref/middleware/#http-strict-transport-security
    if "SECURE_HSTS_SECONDS" in os.environ:
        SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS"))
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

# https://docs.djangoproject.com/en/4.2/ref/settings/#secure-proxy-ssl-header
if "DJANGO_PROXY" in os.environ:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LANGUAGES = [
    (LANGUAGE_CODE, _("English")),
    ("es", _("Spanish")),
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data/media/" if production else ROOT_DIR / "media/")
MEDIA_URL = "media/"

FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
FILE_UPLOAD_TEMP_DIR = os.getenv("FILE_UPLOAD_TEMP_DIR", "/data/tmp/" if production else ROOT_DIR / "tmp/")

ASGI_APPLICATION = "spoonbill_web.asgi.application"


# Dependency configuration

if "SENTRY_DSN" in os.environ:
    # https://docs.sentry.io/platforms/python/logging/#ignoring-a-logger
    ignore_logger("django.security.DisallowedHost")
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0,  # The Sentry plan does not include Performance.
    )

# https://github.com/adamchainz/django-cors-headers
if "CORS_ALLOWED_ORIGINS" in os.environ:
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS").split(",")
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
elif not production:
    CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = [
    *default_headers,
    "Accept-Language",
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.BasicAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# https://docs.celeryq.dev/en/latest/django/first-steps-with-django.html
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BACKEND", "db+postgresql://postgres:postgres@localhost/postgres")

# https://pypi.org/project/channels-redis/
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [CELERY_BROKER_URL],
        },
    },
}

# https://pypi.org/project/django-transfer/
TRANSFER_SERVER = os.getenv("TRANSFER_SERVER", "")
TRANSFER_MAPPINGS = {
    str(MEDIA_ROOT).rstrip("/"): MEDIA_URL.rstrip("/"),
}


# Project configuration

JOB_FILES_TIMEOUT = int(os.getenv("JOB_FILES_TIMEOUT", 1))  # days

DATAREGISTRY_ALLOW_SYMLINKS = "DATAREGISTRY_ALLOW_SYMLINKS" in os.environ

DATAREGISTRY_JAIL = os.getenv("DATAREGISTRY_JAIL", "True") != "False"

DATAREGISTRY_MEDIA_ROOT = os.getenv("DATAREGISTRY_MEDIA_ROOT", "/data/exporter")
if DATAREGISTRY_MEDIA_ROOT:
    DATAREGISTRY_MEDIA_ROOT = Path(DATAREGISTRY_MEDIA_ROOT)
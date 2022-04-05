"""
Django settings for spoonbill_web project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import logging.config
import os
from distutils.util import strtobool
from pathlib import Path

import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger
from yaml import safe_load as load

production = os.getenv("DJANGO_ENV") == "production"

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    # https://docs.sentry.io/platforms/python/logging/#ignoring-a-logger
    ignore_logger("django.security.DisallowedHost")

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0,  # The Sentry plan does not include Performance.
    )

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
root = lambda *x: os.path.join(BASE_DIR, *x)  # noqa

# Logging
LOGGING_CONFIG_PATH = root("settings", "logging.yaml")
with open(LOGGING_CONFIG_PATH, "r") as f:
    LOGGING = load(f.read())

logging.config.dictConfig(LOGGING)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "v3ry$3cr3tk3yf0rdj@ng0")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not production

ALLOWED_HOSTS = [".localhost", "127.0.0.1", "[::1]", "0.0.0.0"]
if "ALLOWED_HOSTS" in os.environ:
    ALLOWED_HOSTS.extend(os.getenv("ALLOWED_HOSTS").split(","))

# Application definition

INSTALLED_APPS = [
    "channels",
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
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "postgres"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

LANGUAGES = [(LANGUAGE_CODE, _("English")), ("es", _("Spanish"))]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOCALE_PATHS = [f"{BASE_DIR}/core/locale", f"{BASE_DIR}/spoonbill_web/locale"]

# Routes
API_PREFIX = os.getenv("API_PREFIX", "api/")
APPEND_SLASH = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/" if not API_PREFIX else f"{API_PREFIX}static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# CORS settings
CORS_ORIGIN_WHITELIST = os.getenv("CORS_ORIGIN_WHITELIST", "http://127.0.0.1:8080,http://localhost:8080").split(",")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST


# Celery config
CELERY_BROKER_URL = os.getenv("CELERY_BROKER", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BACKEND", "db+postgresql://postgres:postgres@localhost/postgres")

JOB_FILES_TIMEOUT = int(os.getenv("JOB_FILES_TIMEOUT", 1))  # days

MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data/media/")
MEDIA_URL = "/media/"

# Managing files
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
FILE_UPLOAD_TEMP_DIR = os.getenv("FILE_UPLOAD_TEMP_DIR", "/data/tmp/")

# Channels
ASGI_APPLICATION = "spoonbill_web.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv("REDIS_HOST", "127.0.0.1"), 6379)],
        },
    },
}

# SSL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django transfer: https://pypi.org/project/django-transfer/
TRANSFER_SERVER = os.getenv("TRANSFER_SERVER", "")
TRANSFER_MAPPINGS = {
    MEDIA_ROOT[:-1]: MEDIA_URL[:-1],
}


DATAREGISTRY_ALLOW_SYMLINKS = bool(strtobool(os.getenv("DATAREGISTRY_ALLOW_SYMLINKS", "False")))

DATAREGISTRY_JAIL = bool(strtobool(os.getenv("DATAREGISTRY_JAIL", "True")))

DATAREGISTRY_MEDIA_ROOT = os.getenv("DATAREGISTRY_MEDIA_ROOT", "/data/exporter")
if DATAREGISTRY_MEDIA_ROOT:
    DATAREGISTRY_MEDIA_ROOT = Path(DATAREGISTRY_MEDIA_ROOT)


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.BasicAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

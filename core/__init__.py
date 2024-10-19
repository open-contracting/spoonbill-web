# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
from core.celery import app as celery_app

__all__ = ("celery_app",)

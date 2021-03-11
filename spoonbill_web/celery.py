import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spoonbill_web.settings.settings")

app = Celery("spoonbill_web")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery(
    "core",
    broker_connection_retry=False,
    broker_connection_retry_on_startup=True,
    broker_channel_error_retry=True,
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

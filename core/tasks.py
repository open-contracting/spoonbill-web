import logging
import shutil
import time
from datetime import datetime
from random import randint

import pytz
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

from core.models import Upload, Validation
from spoonbill_web.celery import app as celery_app

logger = logging.getLogger(__name__)
utc = pytz.UTC


@celery_app.task
def validate_data(upload_id, validation_id):
    upload = Upload.objects.get(id=upload_id)
    validation = Validation.objects.get(id=validation_id)

    timeout = randint(10, 20)
    logger.info(
        "Start validation for %s file with duration about %d sec."
        % (upload.filename, timeout)
    )
    time.sleep(timeout)

    validation.is_valid = True
    validation.save(update_fields=["is_valid"])

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"validate_data_{upload_id}",
        {
            "type": "task.validate",
            "message": {"upload_id": upload_id, "is_valid": True},
        },
    )


@celery_app.task
def cleanup_upload(upload_id):
    """
    Task cleanup all data related to upload id
    """
    upload = Upload.objects.get(id=upload_id)
    if upload.expired_at > utc.localize(datetime.now()):
        logger.info(
            "Skip upload cleanup %s, expired_at in future %s"
            % (upload.id, upload.expired_at.isoformat())
        )
        return
    shutil.rmtree(f"{settings.UPLOAD_PATH_PREFIX}{upload.id}", ignore_errors=True)
    upload.deleted = True
    upload.save(update_fields=["deleted"])
    logger.info("Remove all data from %s%s" % (settings.UPLOAD_PATH_PREFIX, upload.id))

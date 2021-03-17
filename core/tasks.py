import logging
import shutil

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone

from core.models import Upload
from core.serializers import UploadSerializer
from spoonbill_web.celery import app as celery_app

logger = logging.getLogger(__name__)


getters = {"Upload": {"model": Upload, "serializer": UploadSerializer}}


@celery_app.task
def validate_data(object_id, model=None):
    if model not in getters:
        logger.info(
            "Model %s not registered in getters" % model,
            extra={"MESSAGE_ID": "model_not_registered", "TASK": "validation", "MODEL": model, "ID": object_id},
        )
        return
    datasource = getters[model]["model"].objects.get(id=object_id)
    serializer = getters[model]["serializer"]()

    datasource.status = "validation"
    datasource.save(update_fields=["validation"])
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"validate_data_{datasource.id}",
        {"type": "task.validate", "datasource": serializer.to_representation(instance=datasource)},
    )

    logger.info("Start validation for %s file" % object_id)

    datasource.validation.is_valid = True
    datasource.validation.save(update_fields=["is_valid"])

    async_to_sync(channel_layer.group_send)(
        f"validate_data_{datasource.id}",
        {"type": "task.validate", "datasource": serializer.to_representation(instance=datasource)},
    )


@celery_app.task
def cleanup_upload(object_id, model=None):
    """
    Task cleanup all data related to upload id
    """
    if model not in getters:
        logger.info(
            "Model %s not registered in getters" % model,
            extra={"MESSAGE_ID": "model_not_registered", "TASK": "cleanup_upload", "MODEL": model, "ID": object_id},
        )
        return
    datasource = getters[model]["model"].objects.get(id=object_id)
    if datasource.expired_at > timezone.now():
        logger.debug(
            "Skip datasource cleanup %s, expired_at in future %s" % (datasource.id, datasource.expired_at.isoformat())
        )
        return
    shutil.rmtree(f"{settings.UPLOAD_PATH_PREFIX}{datasource.id}", ignore_errors=True)
    datasource.deleted = True
    datasource.save(update_fields=["deleted"])
    logger.info("Remove all data from %s%s" % (settings.UPLOAD_PATH_PREFIX, datasource.id))

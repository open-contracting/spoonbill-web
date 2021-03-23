import logging
import shutil
from datetime import timedelta
from tempfile import TemporaryFile

import ijson
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.models import Upload, Url
from core.serializers import UploadSerializer, UrlSerializer
from spoonbill_web.celery import app as celery_app

logger = logging.getLogger(__name__)

getters = {
    "Upload": {"model": Upload, "serializer": UploadSerializer},
    "Url": {"model": Url, "serializer": UrlSerializer},
}


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

    logger.debug("Start validation for %s file" % object_id)

    is_valid = False
    try:
        with open(datasource.file.path, "rb") as f:
            items = ijson.items(f, "records.item")
            for item in items:
                if item:
                    is_valid = True
                    break
        if not is_valid:
            with open(datasource.file.path, "rb") as f:
                items = ijson.items(f, "releases.item")
                for item in items:
                    if item:
                        is_valid = True
                        break
    except (ijson.JSONError, ijson.IncompleteJSONError) as e:
        logger.info(
            "Error while validating data %s" % object_id,
            extra={"MESSAGE_ID": "validation_exception", "MODEL": model, "ID": object_id, "STR_ERROR": str(e)},
        )

    datasource.validation.is_valid = is_valid
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
    shutil.rmtree(f"{settings.MEDIA_ROOT}{datasource.id}", ignore_errors=True)
    datasource.deleted = True
    datasource.save(update_fields=["deleted"])
    logger.debug("Remove all data from %s%s" % (settings.MEDIA_ROOT, datasource.id))


@celery_app.task
def download_data_source(object_id, model=None):
    if model not in getters:
        logger.info(
            "Model %s not registered in getters" % model,
            extra={
                "MESSAGE_ID": "model_not_registered",
                "TASK": "download_datasource",
                "MODEL": model,
                "ID": object_id,
            },
        )
        return
    try:
        datasource = getters[model]["model"].objects.get(id=object_id)
        serializer = getters[model]["serializer"]()

        datasource.status = "downloading"
        datasource.save(update_fields=["status"])

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"validate_data_{object_id}",
            {
                "type": "task.download_data_source",
                "datasource": serializer.to_representation(instance=datasource),
            },
        )
        logger.debug(
            "Start download for %s" % object_id,
            extra={"MESSAGE_ID": "download_start", "UPLOAD_ID": object_id, "URL": datasource.url},
        )
        r = requests.get(datasource.url, stream=True)
        if r.status_code != 200:
            logger.error(
                "Error while downloading data file for %s" % object_id,
                extra={
                    "MESSAGE_ID": "download_failed",
                    "DATASOURCE_ID": object_id,
                    "MODEL": model,
                    "STATUS_CODE": r.status_code,
                },
            )
            datasource.error = _(f"{r.status_code}: {r.reason}")
            datasource.status = "failed"
            datasource.save(update_fields=["error", "status"])
            async_to_sync(channel_layer.group_send)(
                f"validate_data_{object_id}",
                {
                    "type": "task.download_data_source",
                    "datasource": serializer.to_representation(instance=datasource),
                },
            )
            return
        size = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 10240
        with TemporaryFile() as temp:
            for chunk in r.iter_content(chunk_size=chunk_size):
                temp.write(chunk)
            downloaded += chunk_size
            progress = (downloaded / size) * 100
            progress = progress if progress < 100 else 100
            async_to_sync(channel_layer.group_send)(
                f"validate_data_{object_id}",
                {
                    "type": "task.download_data_source",
                    "datasource": serializer.to_representation(instance=datasource),
                    "progress": int(progress),
                },
            )
            temp.seek(0)
            datasource.file = File(temp)
            datasource.save(update_fields=["file"])

        if datasource.analyzed_data_url:
            r = requests.get(datasource.analyzed_data_url, stream=True)
            if r.status_code != 200:
                logger.error(
                    "Error while downloading data file for %s" % object_id,
                    extra={
                        "MESSAGE_ID": "download_failed",
                        "DATASOURCE_ID": object_id,
                        "MODEL": model,
                        "STATUS_CODE": r.status_code,
                    },
                )
                datasource.error = _(f"{r.status_code}: {r.reason}")
                datasource.status = "failed"
                datasource.save(update_fields=["error", "status"])
                async_to_sync(channel_layer.group_send)(
                    f"validate_data_{object_id}",
                    {
                        "type": "task.download_data_source",
                        "datasource": serializer.to_representation(instance=datasource),
                    },
                )
                return
            downloaded = 0
            datasource.status = "analyzed_data.downloading"
            datasource.save(update_fields=["status"])
            with TemporaryFile() as temp:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    temp.write(chunk)
                downloaded += chunk_size
                progress = (downloaded / size) * 100
                progress = progress if progress < 100 else 100
                async_to_sync(channel_layer.group_send)(
                    f"validate_data_{object_id}",
                    {
                        "type": "task.download_data_source",
                        "datasource": serializer.to_representation(instance=datasource),
                        "progress": int(progress),
                    },
                )
                temp.seek(0)
                datasource.analyzed_file = File(temp)
                datasource.save(update_fields=["analyzed_file"])
        datasource.status = "queued.validation"
        datasource.downloaded = True
        expired_at = timezone.now() + timedelta(days=settings.UPLOAD_TIMEDELTA)
        datasource.expired_at = expired_at
        datasource.save(update_fields=["status", "downloaded", "expired_at"])

        async_to_sync(channel_layer.group_send)(
            f"validate_data_{object_id}",
            {
                "type": "task.download_data_source",
                "datasource": serializer.to_representation(instance=datasource),
            },
        )
        logger.info(
            "Complete download for %s" % object_id,
            extra={
                "MESSAGE_ID": "download_complete",
                "UPLOAD_ID": object_id,
                "URL": datasource.url,
                "EXPIRED_AT": expired_at.isoformat(),
            },
        )
        task = validate_data.delay(object_id, model=model)
        datasource.validation.task_id = task.id
        datasource.validation.save(update_fields=["task_id"])
        logger.info(
            "Schedule validation for %s" % object_id,
            extra={"MESSAGE_ID": "schedule_validation", "UPLOAD_ID": object_id},
        )
    except Exception as e:
        logger.exception(
            "Error while download datasource %s" % object_id,
            extra={"MESSAGE_ID": "download_exception", "DATASOURCE_ID": object_id, "MODEL": model, "ERROR": str(e)},
        )
        datasource.error = _("Something went wrong. Contact with support service.")
        datasource.status = "failed"
        datasource.save(update_fields=["status", "error"])
        async_to_sync(channel_layer.group_send)(
            f"validate_data_{object_id}",
            {
                "type": "task.download_data_source",
                "datasource": serializer.to_representation(instance=datasource),
            },
        )

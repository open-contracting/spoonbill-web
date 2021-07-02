import json
import logging
import os
import pathlib
import shutil
import time
from copy import deepcopy
from datetime import timedelta
from urllib.parse import unquote, urlparse

import ijson
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from spoonbill import FileAnalyzer, FileFlattener
from spoonbill.common import COMBINED_TABLES, ROOT_TABLES
from spoonbill.flatten import FlattenOptions
from spoonbill.stats import DataPreprocessor

from core.models import Flatten, Upload, Url
from core.serializers import FlattenSerializer, UploadSerializer, UrlSerializer
from core.utils import (
    dataregistry_path_formatter,
    dataregistry_path_resolver,
    get_flatten_options,
    get_protocol,
    internationalization,
    retrieve_tables,
    zip_files,
)
from spoonbill_web.celery import app as celery_app

DATA_DIR = os.path.dirname(__file__) + "/data"
SCHEMA_PATH = f"{DATA_DIR}/schema.json"
getters = {
    "Upload": {"model": Upload, "serializer": UploadSerializer},
    "Url": {"model": Url, "serializer": UrlSerializer},
}
logger = logging.getLogger(__name__)


def get_serializer_by_model(str_model, log_context=None):
    """
    Utility for return model and serializer by string model value

    :param str_model: String value (name) of model class
    :return: tuple with model and serializer
    """
    if str_model not in getters:
        extra = {"MESSAGE_ID": "model_not_registered", "MODEL": str_model}
        if log_context:
            extra.update(log_context)
        logger.info(
            "Model %s not registered in getters" % str_model,
            extra=extra,
        )
        return None, None
    else:
        return getters[str_model]["model"], getters[str_model]["serializer"]()


@celery_app.task
def validate_data(object_id, model=None, lang_code="en"):
    with internationalization(lang_code=lang_code):
        logger_context = {"DATASOURCE_ID": object_id, "TASK": "validate_data"}
        ds_model, serializer = get_serializer_by_model(model, logger_context)
        channel_layer = get_channel_layer()
        if not ds_model:
            async_to_sync(channel_layer.group_send)(
                f"datasource_{object_id}",
                {"type": "task.validate", "error": _("Model %s for datasource not found") % model},
            )
            return
        try:
            is_valid = False
            datasource = ds_model.objects.get(id=object_id)

            datasource.status = "validation"
            datasource.save(update_fields=["status"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.validate", "datasource": serializer.to_representation(instance=datasource)},
            )

            logger.debug("Start validation for %s file" % object_id)
            paths = (
                datasource.paths
                if hasattr(datasource, "paths") and datasource.paths
                else [pathlib.Path(datasource.file.path)]
            )
            workdir = (
                pathlib.Path(paths[0]).parent
                if hasattr(datasource, "paths") and datasource.paths
                else pathlib.Path(datasource.file.path).parent
            )
            filenames = [pathlib.Path(path).name for path in paths]
            total = (
                pathlib.Path(paths[0]).stat().st_size
                if hasattr(datasource, "paths") and datasource.paths
                else pathlib.Path(datasource.file.path).stat().st_size
            )
            analyzer = FileAnalyzer(workdir, root_tables=ROOT_TABLES, combined_tables=COMBINED_TABLES)

            timestamp = time.time()

            filepaths = [workdir / filename for filename in filenames]

            for read, count in analyzer.analyze_file(filepaths, with_preview=True):
                if (time.time() - timestamp) <= 1:
                    continue
                async_to_sync(channel_layer.group_send)(
                    f"datasource_{datasource.id}",
                    {
                        "type": "task.validate",
                        "datasource": {"id": str(datasource.id)},
                        "progress": {
                            "rows": count,
                            "percentage": (read / total) * 100 if total else 0,
                            "size": total,
                            "read": read,
                        },
                    },
                )
                timestamp = time.time()
            is_valid = True

            datasource.validation.is_valid = is_valid
            datasource.root_key = analyzer.pkg_type
            datasource.validation.save(update_fields=["is_valid"])
            datasource.save(update_fields=["root_key"])

            if is_valid and not datasource.available_tables and not datasource.analyzed_file:
                _file = ContentFile(b"")
                datasource.analyzed_file.save("new", _file)
                analyzer.spec.dump(datasource.analyzed_file.path)
                available_tables, unavailable_tables = retrieve_tables(analyzer.spec)
                datasource.available_tables = available_tables
                datasource.unavailable_tables = unavailable_tables
                datasource.save(update_fields=["available_tables", "unavailable_tables"])
            elif is_valid and datasource.analyzed_file:
                spec = DataPreprocessor.restore(datasource.analyzed_file.path)
                available_tables, unavailable_tables = retrieve_tables(spec)
                datasource.available_tables = available_tables
                datasource.unavailable_tables = unavailable_tables
                datasource.save(update_fields=["available_tables", "unavailable_tables"])

            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.validate", "datasource": serializer.to_representation(instance=datasource)},
            )
        except ObjectDoesNotExist:
            logger_context["MODEL"] = model
            logger_context["MESSAGE_ID"] = "datasource_not_found"
            logger.info("Datasource %s %s not found" % (model, object_id), extra=logger_context)
            async_to_sync(channel_layer.group_send)(
                f"datasource_{object_id}",
                {"type": "task.validate", "error": _("Datasource %s not found") % object_id},
            )
        except (ijson.JSONError, ijson.IncompleteJSONError) as e:
            logger.info(
                "Error while validating data %s" % object_id,
                extra={"MESSAGE_ID": "validation_exception", "MODEL": model, "ID": object_id, "STR_ERROR": str(e)},
            )
            message = _("Error while validating data `%s`") % str(e)
            datasource.validation.errors = message
            datasource.validation.is_valid = False
            datasource.validation.save(update_fields=["errors", "is_valid"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.validate", "error": message},
            )
        except OSError as e:
            logger.exception(
                "Error while validating data %s" % object_id,
                extra={"MESSAGE_ID": "validation_exception", "MODEL": model, "ID": object_id, "STR_ERROR": str(e)},
            )
            message = _("Currently, the space limit was reached. Please try again later.")
            datasource.validation.errors = message
            datasource.validation.is_valid = False
            datasource.validation.save(update_fields=["errors", "is_valid"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.validate", "error": message},
            )
        except Exception as e:
            logger.exception(
                "Error while validating data %s" % object_id,
                extra={"MESSAGE_ID": "validation_exception", "MODEL": model, "ID": object_id, "STR_ERROR": str(e)},
            )
            message = _("Error while validating data `%s`") % str(e)
            datasource.validation.errors = message
            datasource.validation.is_valid = False
            datasource.validation.save(update_fields=["errors", "is_valid"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.validate", "error": message},
            )


@celery_app.task
def cleanup_upload(object_id, model=None, lang_code="en"):
    """
    Task cleanup all data related to upload id
    """
    with internationalization(lang_code=lang_code):
        logger_context = {"DATASOURCE_ID": object_id, "TASK": "cleanup_upload"}
        ds_model, _ = get_serializer_by_model(model, logger_context)
        if not ds_model:
            return
        try:
            datasource = ds_model.objects.get(id=object_id)
        except ObjectDoesNotExist:
            logger_context["MODEL"] = model
            logger_context["MESSAGE_ID"] = "datasource_not_found"
            logger.info("Datasource %s %s not found" % (model, object_id), extra=logger_context)
            return
        if datasource.expired_at > timezone.now():
            logger.debug(
                "Skip datasource cleanup %s, expired_at in future %s"
                % (datasource.id, datasource.expired_at.isoformat())
            )
            cleanup_upload.apply_async((datasource.id, model, lang_code), eta=datasource.expired_at)
            return
        datasource_path = os.path.dirname(datasource.file.path)
        shutil.rmtree(datasource_path, ignore_errors=True)
        datasource.delete()
        logger.debug("Remove all data from %s" % (datasource_path))


@celery_app.task
def download_data_source(object_id, model=None, lang_code="en"):
    with internationalization(lang_code=lang_code):
        logger_context = {"DATASOURCE_ID": object_id, "TASK": "download_data_source"}
        channel_layer = get_channel_layer()
        ds_model, serializer = get_serializer_by_model(model, logger_context)
        if not ds_model or not serializer:
            async_to_sync(channel_layer.group_send)(
                f"datasource_{object_id}",
                {"type": "task.download_data_source", "error": _("Model %s for datasource not found") % model},
            )
            return
        try:
            datasource = ds_model.objects.get(id=object_id)

            datasource.status = "downloading"
            datasource.save(update_fields=["status"])

            async_to_sync(channel_layer.group_send)(
                f"datasource_{object_id}",
                {
                    "type": "task.download_data_source",
                    "datasource": serializer.to_representation(instance=datasource),
                },
            )
            logger.debug(
                "Start download for %s" % object_id,
                extra={"MESSAGE_ID": "download_start", "UPLOAD_ID": object_id, "URL": datasource.url},
            )

            urls = [datasource.url] if not isinstance(datasource.url, list) else datasource.url
            if get_protocol(urls[0]) == "file":
                datasource.paths = [dataregistry_path_resolver(dataregistry_path_formatter(url)) for url in urls]
                datasource.save()
            else:
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
                        f"datasource_{object_id}",
                        {
                            "type": "task.download_data_source",
                            "datasource": serializer.to_representation(instance=datasource),
                        },
                    )
                    return
                size = int(r.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 10240
                _file = ContentFile(b"")
                datasource.file.save("new", _file)
                with open(datasource.file.path, "wb") as fd:
                    timestamp = time.time()
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        fd.write(chunk)
                        downloaded += chunk_size
                        if size != 0:
                            progress = (downloaded / size) * 100
                            progress = progress if progress < 100 else 100
                        else:
                            progress = size
                        if (time.time() - timestamp) <= 1:
                            continue
                        async_to_sync(channel_layer.group_send)(
                            f"datasource_{object_id}",
                            {
                                "type": "task.download_data_source",
                                "datasource": serializer.to_representation(instance=datasource),
                                "progress": int(progress),
                            },
                        )
                        timestamp = time.time()
            if datasource.analyzed_data_url:
                if get_protocol(datasource.analyzed_data_url) == "file":
                    path = dataregistry_path_formatter(datasource.analyzed_data_url)
                    path = dataregistry_path_resolver(path)
                    path = str(path).replace(settings.MEDIA_ROOT, "")
                    datasource.analyzed_file.name = path
                    datasource.save()
                else:
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
                            f"datasource_{object_id}",
                            {
                                "type": "task.download_data_source",
                                "datasource": serializer.to_representation(instance=datasource),
                            },
                        )
                        return
                    downloaded = 0
                    datasource.status = "analyzed_data.downloading"
                    datasource.save(update_fields=["status"])
                    _file = ContentFile(b"")
                    datasource.analyzed_file.save("new", _file)
                    with open(datasource.analyzed_file.path, "wb") as fd:
                        timestamp = time.time()
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            fd.write(chunk)
                            downloaded += chunk_size
                            progress = (downloaded / size) * 100
                            progress = progress if progress < 100 else 100
                            if (time.time() - timestamp) <= 1:
                                continue
                            async_to_sync(channel_layer.group_send)(
                                f"datasource_{object_id}",
                                {
                                    "type": "task.download_data_source",
                                    "datasource": serializer.to_representation(instance=datasource),
                                    "progress": int(progress),
                                },
                            )
                            timestamp = time.time()

            datasource.status = "queued.validation"
            datasource.downloaded = True
            expired_at = timezone.now() + timedelta(days=settings.JOB_FILES_TIMEOUT)
            datasource.expired_at = expired_at
            datasource.save(update_fields=["status", "downloaded", "expired_at"])

            async_to_sync(channel_layer.group_send)(
                f"datasource_{object_id}",
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
        except ObjectDoesNotExist:
            logger_context["MODEL"] = model
            logger_context["MESSAGE_ID"] = "datasource_not_found"
            logger.info("Datasource %s %s not found" % (model, object_id), extra=logger_context)
            async_to_sync(channel_layer.group_send)(
                f"datasource_{object_id}",
                {"type": "task.download_data_source", "error": _("Datasource %s not found") % object_id},
            )
        except (OSError, Exception) as e:
            e = type(e).__name__
            message_id = {"OSError": "download_no_left_space", "Exception": "download_exception"}
            message = {
                "OSError": "Currently, the space limit was reached. Please try again later.",
                "Exception": "Something went wrong. Contact with support service.",
            }
            log_level = {"OSError": logger.info, "Exception": logger.exception}
            log_level[e](
                "Error while download datasource %s" % object_id,
                extra={
                    "MESSAGE_ID": message_id[e],
                    "DATASOURCE_ID": object_id,
                    "MODEL": model,
                    "ERROR": str(e),
                },
            )
            datasource.error = _(message[e])
            datasource.status = "failed"
            datasource.save(update_fields=["status", "error"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{object_id}",
                {
                    "type": "task.download_data_source",
                    "datasource": serializer.to_representation(instance=datasource),
                },
            )


@celery_app.task
def flatten_data(flatten_id, model=None, lang_code="en_US"):
    with internationalization(lang_code=lang_code):
        logger_context = {"FLATTEN_ID": flatten_id, "TASK": "flatten_data", "MODEL": model}
        channel_layer = get_channel_layer()
        if model not in getters:
            extra = {
                "MESSAGE_ID": "model_not_registered",
                "MODEL": model,
                "TASK": "flatten_data",
                "FLATTEN_ID": flatten_id,
            }
            logger.info("Model %s not registered in getters" % model, extra=extra)
            return
        try:
            serializer = FlattenSerializer()
            flatten = Flatten.objects.get(id=flatten_id)
            selection = flatten.dataselection_set.all()[0]
            datasource = getattr(selection, f"{model.lower()}_set").all()[0]
            flatten.status = "processing"
            flatten.save(update_fields=["status"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.flatten", "flatten": serializer.to_representation(instance=flatten)},
            )
            spec = DataPreprocessor.restore(datasource.analyzed_file.path)
            total_rows = spec.total_items
            opt = get_flatten_options(selection)
            logger.debug(
                "Generate options for export",
                extra={
                    "MESSAGE_ID": "generate_flatten_options",
                    "DATASOURCE_ID": str(datasource.id),
                    "MODEL": model,
                    "SELECTION_ID": str(selection.id),
                    "FLATTEN_ID": str(flatten.id),
                    "OPTIONS": opt,
                },
            )
            options = FlattenOptions(**opt)
            workdir = (
                pathlib.Path(datasource.file.path).parent
                if datasource.file
                else pathlib.Path(datasource.paths[0]).parent
            )
            formats = {"csv": None, "xlsx": None}
            if flatten.export_format == flatten.CSV:
                workdir = workdir / "export"
                if not workdir.exists():
                    os.makedirs(workdir)
                formats[flatten.export_format] = workdir
            else:
                formats[flatten.export_format] = "result.xlsx"
            flattener = FileFlattener(
                workdir,
                options,
                tables=spec.tables,
                pkg_type=datasource.root_key,
                multiple_values=getattr(spec, "multiple_values", False),
                **formats,
            )
            timestamp = time.time()

            files = datasource.paths if hasattr(datasource, "paths") and datasource.paths else [datasource.file.path]

            for count in flattener.flatten_file(files):
                if (time.time() - timestamp) <= 1:
                    continue
                async_to_sync(channel_layer.group_send)(
                    f"datasource_{datasource.id}",
                    {
                        "type": "task.flatten",
                        "flatten": {"id": str(flatten.id)},
                        "progress": {
                            "total_rows": total_rows,
                            "processed": count,
                            "percentage": (count / total_rows) * 100 if total_rows else total_rows,
                        },
                    },
                )
                timestamp = time.time()
            if flatten.export_format == flatten.CSV:
                target_file = f"{workdir}/{datasource.id}.zip"
                zip_files(workdir, target_file, extension="csv")
                with open(target_file, "rb") as fd:
                    file_ = File(fd)
                    file_.name = f"{datasource.id}.zip"
                    flatten.file = file_
                    flatten.status = "completed"
                    flatten.save(update_fields=["file", "status"])
                os.remove(fd.name)
            else:
                target_file = f"{workdir}/result.xlsx"
                with open(target_file, "rb") as fd:
                    file_ = File(fd)
                    file_.name = "result.xlsx"
                    flatten.file = file_
                    flatten.status = "completed"
                    flatten.save(update_fields=["file", "status"])
                os.remove(fd.name)
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.flatten", "flatten": serializer.to_representation(instance=flatten)},
            )
        except ObjectDoesNotExist:
            extra = deepcopy(logger_context)
            extra["MESSAGE_ID"] = "flatten_not_found"
            logger.info("Flatten %s for %s model not found" % (flatten_id, model), extra=extra)
        except OSError as e:
            extra = deepcopy(logger_context)
            extra.update(
                {"MESSAGE_ID": "flatten_no_left_space", "DATASOURCE_ID": str(datasource.id), "ERROR_MSG": str(e)}
            )
            logger.info("Flatten %s for %s model failed: %s" % (flatten_id, model, e), extra=extra)
            flatten.status = "failed"
            flatten.error = _("Currently, the space limit was reached. Please try again later.")
            flatten.save(update_fields=["error", "status"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.flatten", "flatten": serializer.to_representation(instance=flatten)},
            )
        except (TypeError, Exception) as e:
            error_message = str(e)
            extra = deepcopy(logger_context)
            extra["MESSAGE_ID"] = "flatten_failed"
            extra["ERROR_MESSAGE"] = error_message
            logger.error(
                "Flatten %s for %s datasource %s failed" % (flatten_id, model, datasource.id),
                extra=extra,
                exc_info=True,
            )
            flatten.status = "failed"
            flatten.error = error_message
            flatten.save(update_fields=["error", "status"])
            async_to_sync(channel_layer.group_send)(
                f"datasource_{datasource.id}",
                {"type": "task.flatten", "flatten": serializer.to_representation(instance=flatten)},
            )

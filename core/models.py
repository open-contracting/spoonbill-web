import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.utils import instance_directory_path

fs = FileSystemStorage()


# Create your models here.
class Validation(models.Model):
    """
    Validation object will store information about validation file job state
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    task_id = models.CharField(max_length=36, blank=True, null=True)
    is_valid = models.BooleanField(blank=True, null=True)
    errors = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "validations"
        verbose_name = _("Validation")
        verbose_name_plural = _("Validations")


class Upload(models.Model):
    """
    Upload object will store all information about received file and related processes.
    """

    QUEUED_VALIDATION = "queued.validation"
    VALIDATION = "validation"
    STATUS_CHOICES = [
        (QUEUED_VALIDATION, _("Queued validation")),
        (VALIDATION, _("Validation")),
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    file = models.FileField(upload_to=instance_directory_path, storage=fs)
    analyzed_file = models.FileField(upload_to=instance_directory_path, blank=True, null=True, storage=fs)
    validation = models.ForeignKey("Validation", blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=QUEUED_VALIDATION)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    selections = models.ManyToManyField("DataSelection", blank=True)
    available_tables = ArrayField(models.JSONField(default=dict), blank=True, null=True)

    class Meta:
        db_table = "uploads"
        verbose_name = _("Upload")
        verbose_name_plural = _("Uploads")


class Url(models.Model):

    QUEUED_DOWNLOAD = "queued.download"
    DOWNLOADING = "downloading"
    ANALYZED_DATA_DOWNLOADING = "analyzed_data.downloading"
    QUEUED_VALIDATION = "queued.validation"
    VALIDATION = "validation"
    FAILED = "failed"
    STATUS_CHOICES = [
        (QUEUED_DOWNLOAD, _("Queued download")),
        (ANALYZED_DATA_DOWNLOADING, _("Downloading analyzed data")),
        (DOWNLOADING, _("Downloading")),
        (QUEUED_VALIDATION, _("Queued validation")),
        (VALIDATION, _("Validation")),
        (FAILED, _("Failed")),
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    url = models.URLField()
    analyzed_data_url = models.URLField(blank=True, null=True)
    analyzed_file = models.FileField(upload_to=instance_directory_path, blank=True, null=True, storage=fs)
    file = models.FileField(upload_to=instance_directory_path, blank=True, null=True, storage=fs)
    validation = models.ForeignKey("Validation", blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=QUEUED_DOWNLOAD)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    downloaded = models.BooleanField(default=False)
    error = models.TextField(blank=True, null=True)
    selections = models.ManyToManyField("DataSelection", blank=True)
    available_tables = ArrayField(models.JSONField(default=dict), blank=True, null=True)

    class Meta:
        db_table = "urls"
        verbose_name = _("Url")
        verbose_name_plural = _("Urls")


class DataSelection(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tables = models.ManyToManyField("Table", blank=True)

    class Meta:
        db_table = "data_selections"
        verbose_name = _("Data Selection")
        verbose_name_plural = _("Data Selections")


class Table(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=120)
    split = models.BooleanField(default=False)
    include = models.BooleanField(default=True)

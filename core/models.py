import os
import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import export_directory_path, instance_directory_path
from core.validators import validate_url_or_path

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

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


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
    unavailable_tables = ArrayField(models.CharField(max_length=50), default=list)
    root_key = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "uploads"
        verbose_name = _("Upload")
        verbose_name_plural = _("Uploads")

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


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
    url = models.CharField(max_length=2048, validators=[validate_url_or_path])
    analyzed_data_url = models.CharField(max_length=2048, validators=[validate_url_or_path], blank=True, null=True)
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
    unavailable_tables = ArrayField(models.CharField(max_length=50), default=list)
    root_key = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=60, blank=True, null=True)
    period = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    is_head_of_multi_upload = models.BooleanField(default=False)
    multi_uploads = models.ManyToManyField("self", blank=True, null=True)

    class Meta:
        db_table = "urls"
        verbose_name = _("Url")
        verbose_name_plural = _("Urls")

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


class DataSelection(models.Model):

    OCDS = "ocds"
    EN_USER_FRIENDLY = "en_user_friendly"
    EN_R_FRIENDLY = "en_r_friendly"
    ES_USER_FRIENDLY = "es_user_friendly"
    ES_R_FRIENDLY = "es_r_friendly"
    CUSTOM = "custom"
    OCDS_LITE = "ocds_lite"
    KIND_CHOICES = [(CUSTOM, _("Custom")), (OCDS_LITE, _("OCDS Lite"))]
    HEADING_TYPES = [
        (OCDS, _("Apply OCDS headings only")),
        (EN_USER_FRIENDLY, _("Apply English user friendly headings to all tables")),
        (EN_R_FRIENDLY, _("Apply English R friendly headings to all tables")),
        (ES_USER_FRIENDLY, _("Apply Spanish user friendly headings to all tables")),
        (ES_R_FRIENDLY, _("Apply Spanish R friendly headings to all tables")),
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tables = models.ManyToManyField("Table")
    headings_type = models.CharField(max_length=30, choices=HEADING_TYPES, default=OCDS)
    flattens = models.ManyToManyField("Flatten", blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=CUSTOM)

    class Meta:
        db_table = "data_selections"
        verbose_name = _("Data Selection")
        verbose_name_plural = _("Data Selections")

    @property
    def flatten_types(self):
        return [f.export_format for f in self.flattens.all()]

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


class Table(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=120)
    split = models.BooleanField(default=False)
    include = models.BooleanField(default=True)
    heading = models.CharField(max_length=31, blank=True, null=True)
    array_tables = models.ManyToManyField("self", blank=True)
    column_headings = models.JSONField(default=dict, encoder=DjangoJSONEncoder, blank=True, null=True)

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


class Flatten(models.Model):

    CSV = "csv"
    XLSX = "xlsx"
    EXPORT_FORMATS = [(CSV, _("A comma-separated values (CSV) file")), (XLSX, _("XLSX (Excel) file format"))]

    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    STATUS_CHOICES = [
        (COMPLETED, _("Completed")),
        (FAILED, _("Failed")),
        (PROCESSING, _("Processing")),
        (SCHEDULED, _("Scheduled")),
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS, default=XLSX)
    file = models.FileField(upload_to=export_directory_path, blank=True, null=True, storage=fs)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=SCHEDULED)
    error = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"

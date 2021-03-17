import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


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
    filename = models.CharField(max_length=64)
    validation = models.ForeignKey("Validation", blank=True, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=QUEUED_VALIDATION)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "uploads"
        verbose_name = _("Upload")
        verbose_name_plural = _("Uploads")

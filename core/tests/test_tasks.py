from datetime import timedelta

import pytest
from django.utils import timezone

from core.models import Upload, Validation
from core.tasks import cleanup_upload, validate_data


@pytest.mark.django_db
class TestValidateDataTask:
    def test_success(self, mocked_sleep):
        validation = Validation.objects.create()
        upload = Upload.objects.create(filename="don.json", validation=validation)

        assert upload.validation.is_valid is None

        validate_data(upload.id, validation.id)

        upload = Upload.objects.get(id=upload.id)
        assert upload.validation.is_valid


@pytest.mark.django_db
class TestCleanupUploadTask:
    def test_success(self):
        expired_at = timezone.now()
        validation = Validation.objects.create()
        upload = Upload.objects.create(filename="don.json", validation=validation, expired_at=expired_at)
        assert not upload.deleted

        cleanup_upload(upload.id)
        upload = Upload.objects.get(id=upload.id)
        assert upload.deleted

    def test_skip_cleanup(self):
        expired_at = timezone.now() + timedelta(minutes=1)
        validation = Validation.objects.create()
        upload = Upload.objects.create(filename="don.json", validation=validation, expired_at=expired_at)
        assert not upload.deleted

        cleanup_upload(upload.id)
        upload = Upload.objects.get(id=upload.id)
        assert not upload.deleted

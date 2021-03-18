import json
from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from core.models import Upload, Url, Validation
from core.tasks import cleanup_upload, download_data_source, validate_data

from .utils import Response


@pytest.mark.django_db
class TestValidateDataTask:
    def test_success(self, upload_obj):
        upload = Upload.objects.get(id=upload_obj.id)

        assert upload.validation.is_valid is None

        validate_data(upload.id, model="Upload")

        upload = Upload.objects.get(id=upload.id)
        assert upload.validation.is_valid

    def test_unregistered_model(self, url_obj):
        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.validation.is_valid is None

        validate_data(url_obj.id, model="SomeNew")
        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.validation.is_valid is None


@pytest.mark.django_db
class TestCleanupUploadTask:
    def test_success(self, upload_obj):
        expired_at = timezone.now()
        upload_obj.expired_at = expired_at
        upload_obj.save(update_fields=["expired_at"])
        assert not upload_obj.deleted

        cleanup_upload(upload_obj.id, model="Upload")
        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert upload_obj.deleted

    def test_skip_cleanup(self, upload_obj):
        expired_at = timezone.now() + timedelta(minutes=1)
        upload_obj.expired_at = expired_at
        upload_obj.save(update_fields=["expired_at"])
        assert not upload_obj.deleted

        cleanup_upload(upload_obj.id, model="Upload")
        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert not upload_obj.deleted

    def test_unregistered_model(self, upload_obj, mocker):
        shutil = mocker.patch("core.tasks.shutil")
        cleanup_upload(upload_obj.id, model="SomeNew")
        assert shutil.rmtree.call_count == 0


@pytest.mark.django_db
class TestDownloadDataSource:
    def test_success(self, mocked_request, url_obj, dataset):
        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "queued.download"
        assert not url_obj.downloaded

        download_data_source(url_obj.id, model="Url")
        url_obj = Url.objects.get(id=url_obj.id)

        assert url_obj.status == "queued.validation"
        assert url_obj.downloaded

        test_dataset = json.loads(dataset.read())
        with open(url_obj.data_file.path) as f:
            data = json.loads(f.read())
        assert data == test_dataset

        with open(url_obj.analyzed_data_file.path) as f:
            data = json.loads(f.read())
        assert data == test_dataset

    def test_unregistered_model(self, mocked_request, url_obj):
        download_data_source(url_obj.id, model="SomeNew")

        assert mocked_request.get.call_count == 0

    def test_fail_request_on_data_download(self, mocked_request, url_obj):
        response = Response(status_code=403)
        mocked_request.get.side_effect = [response]

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "queued.download"
        assert not url_obj.downloaded
        download_data_source(url_obj.id, model="Url")

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "failed"
        assert url_obj.error == f"{response.status_code}: {response.reason}"
        assert mocked_request.get.call_count == 1

    def test_fail_request_on_analyzed_data_download(self, mocked_request, url_obj, dataset):
        response = Response(status_code=403)
        success_response = mocked_request.get.return_value
        mocked_request.get.side_effect = [success_response, response]

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "queued.download"
        assert not url_obj.downloaded
        download_data_source(url_obj.id, model="Url")

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "failed"
        assert url_obj.error == f"{response.status_code}: {response.reason}"
        assert mocked_request.get.call_count == 2

        with open(url_obj.data_file.path) as f:
            data = json.loads(f.read())
        assert data == json.loads(dataset.read())

    def test_exception_on_analyzed_data_download(self, mocked_request, url_obj, dataset):
        success_response = mocked_request.get.return_value
        mocked_request.get.side_effect = [success_response, Exception("Some error from remote host")]

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "queued.download"
        assert not url_obj.downloaded
        download_data_source(url_obj.id, model="Url")

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "failed"
        assert url_obj.error == "Something went wrong. Contact with support service."
        assert mocked_request.get.call_count == 2

        with open(url_obj.data_file.path) as f:
            data = json.loads(f.read())
        assert data == json.loads(dataset.read())

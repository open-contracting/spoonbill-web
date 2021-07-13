import errno
import gzip
import os
import pathlib
import shutil
from unittest.mock import patch

import pytest
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework import status

from core.models import DataFile, Upload
from core.serializers import UploadSerializer
from core.tests.utils import create_data_selection, get_data_selections

from .utils import Task

DATA_DIR = os.path.dirname(__file__) + "/data"
DATASET_PATH = f"{DATA_DIR}/sample-dataset.json"
DATASET_PATH_JSONL = f"{DATA_DIR}/sample-dataset.jsonl"
DATASET_PATH_GZ = f"{DATA_DIR}/sample-dataset.json.gz"
PATHS = {DATASET_PATH: open, DATASET_PATH_JSONL: open, DATASET_PATH_GZ: gzip.open}


@pytest.mark.django_db
class TestUploadViews:
    @pytest.fixture(autouse=True)
    def use_fixtures(
        self, upload_obj, upload_obj_validated, validation_task, cleanup_upload_task, dataset, settings, mocker, client
    ):
        self.url_prefix = "/uploads/" if not settings.API_PREFIX else f"/{settings.API_PREFIX}uploads/"
        self.dataset = dataset
        self.task_cleanup = cleanup_upload_task
        self.task_validation = validation_task
        self.datasource = upload_obj
        self.validated_datasource = upload_obj_validated
        self.mocker = mocker
        self.client = client
        self.settings = settings

    def test_create_upload_wo_file(self):
        response = self.client.post(self.url_prefix, {"attr": "value"})
        assert response.status_code == 400
        assert response.json() == {"detail": "File is required"}

    def test_create_upload_successful(self):
        response = self.client.post(self.url_prefix, {"files": self.dataset})
        assert response.status_code == 201
        upload = response.json()
        assert set(upload.keys()) == {
            "analyzed_file",
            "available_tables",
            "created_at",
            "deleted",
            "expired_at",
            "files",
            "id",
            "root_key",
            "selections",
            "status",
            "unavailable_tables",
            "validation",
            "order",
        }
        assert set(upload["validation"].keys()) == {"id", "task_id", "is_valid", "errors"}

        for file in upload["files"]:
            assert file.startswith(settings.MEDIA_URL)
        assert not upload["deleted"]

        upload_obj = Upload.objects.get(id=upload["id"])
        self.task_validation.delay.assert_called_once_with(upload_obj.id, model="Upload", lang_code="en-us")
        self.task_cleanup.apply_async.assert_called_once_with(
            (upload_obj.id, "Upload", "en-us"), eta=upload_obj.expired_at
        )

        # cleanup test data
        shutil.rmtree(f"{self.settings.MEDIA_ROOT}{upload_obj.files.all()[0].id}")

    def test_get_non_existed_upload(self):
        response = self.client.get(f"{self.url_prefix}some-invalid-id/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_get_upload_successful(self):
        response = self.client.get(f"{self.url_prefix}{self.datasource.id}/")
        assert response.status_code == 200
        assert UploadSerializer(self.datasource).data == response.json()

    def test_create_selections_successful(self):
        create_data_selection(self.client, self.datasource, self.url_prefix)

    def test_create_selections_failed(self):
        url = f"{self.url_prefix}{self.datasource.id}/selections/"
        data = {"tables": "name"}
        response = self.client.post(url, content_type="application/json", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"tables": {"non_field_errors": ['Expected a list of items but got type "str".']}}
        }

        data = {"tables": []}
        response = self.client.post(url, content_type="application/json", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": {"tables": {"non_field_errors": ["This list may not be empty."]}}}

    def test_get_selections_successful(self):
        get_data_selections(self.client, self.datasource, self.url_prefix)

    def test_exception_handle(self):
        self.task_cleanup.apply_async.side_effect = Exception("Something went wrong.")
        response = self.client.post(self.url_prefix, {"files": self.dataset})
        assert response.status_code == 500
        assert "detail" in response.json()

    def test_no_left_space(self):
        self.task_cleanup.apply_async.side_effect = OSError(errno.ENOSPC, "No left space.")
        response = self.client.post(self.url_prefix, {"files": self.dataset})
        assert response.status_code == 413
        assert response.json() == {"detail": "Currently, the space limit was reached. Please try again later."}


@pytest.mark.django_db
class TestUploadViewsUnit(TestCase):
    def setUp(self):
        self.url_prefix = "/uploads/" if not settings.API_PREFIX else f"/{settings.API_PREFIX}uploads/"

    @override_settings()
    @patch("core.views.validate_data")
    @patch("core.views.cleanup_upload")
    def test_create_selections_successful(self, mocked_cleanup, mocked_validation):
        for path, reader in PATHS.items():
            settings.FILE_UPLOAD_MAX_MEMORY_SIZE = 100
            mocked_validation.delay.return_value = Task()
            with reader(path) as _file:
                response = self.client.post(self.url_prefix, {"files": _file})
            assert response.status_code == 201
            upload = response.json()
            assert set(upload.keys()) == {
                "analyzed_file",
                "available_tables",
                "created_at",
                "deleted",
                "expired_at",
                "files",
                "id",
                "root_key",
                "selections",
                "status",
                "unavailable_tables",
                "validation",
                "order",
            }
            assert set(upload["validation"].keys()) == {"id", "task_id", "is_valid", "errors"}
            for file in upload["files"]:
                assert file.startswith(settings.MEDIA_URL)
            assert not upload["deleted"]

            upload_obj = Upload.objects.get(id=upload["id"])

            # cleanup test data
            directory = pathlib.Path(upload_obj.files.all()[0].file.path).parent
            shutil.rmtree(directory)

    def test_upload_multiple_files(self):
        with open(DATASET_PATH) as _file:
            response = self.client.post(self.url_prefix, {"files": [_file, _file]})
        assert response.status_code == 413
        assert response.json() == {"detail": "Multi-upload feature is not available for file uploads yet. Stay tuned!"}

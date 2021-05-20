import errno
import json
from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from core.models import DataSelection, Flatten, Upload, Url
from core.tasks import cleanup_upload, download_data_source, flatten_data, validate_data

from .utils import Response, create_flatten


class BaseUploadTestSuite:
    model = "Upload"


@pytest.mark.django_db
class TestValidateDataTask(BaseUploadTestSuite):
    def test_upload_success(self, upload_obj):
        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert upload_obj.validation.is_valid is None
        assert not upload_obj.available_tables

        validate_data(upload_obj.id, model="Upload")

        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert upload_obj.validation.is_valid
        assert len(upload_obj.available_tables) == 8

    def test_url_success(self, url_obj_w_files):
        url_obj_w_files = Url.objects.get(id=url_obj_w_files.id)
        assert url_obj_w_files.validation.is_valid is None
        assert not url_obj_w_files.available_tables

        validate_data(url_obj_w_files.id, model="Url")

        url_obj_w_files = Url.objects.get(id=url_obj_w_files.id)
        assert url_obj_w_files.validation.is_valid
        assert len(url_obj_w_files.available_tables) == 8
        assert url_obj_w_files.available_tables[0]["name"] == "parties"
        assert url_obj_w_files.available_tables[0]["rows"] == 8
        assert url_obj_w_files.available_tables[0]["arrays"] == {}
        assert url_obj_w_files.available_tables[0]["available_data"]["columns"]["total"] == 26
        assert url_obj_w_files.available_tables[0]["available_data"]["columns"]["available"] == 21
        assert url_obj_w_files.available_tables[0]["available_data"]["columns"]["additional"] == ["/parties/test"]
        assert set(url_obj_w_files.available_tables[0]["available_data"]["columns"]["missing_data"]) == {
            "/parties/identifier/uri",
            "/parties/additionalIdentifiers/0/id",
            "/parties/additionalIdentifiers/0/legalName",
            "/parties/additionalIdentifiers/0/scheme",
            "/parties/additionalIdentifiers/0/uri",
        }

    # def test_json_w_records(self, upload_obj):
    #     with open(upload_obj.file.path, "w") as f:
    #         f.write('{"records": ["record"]}')

    #     upload_obj = Upload.objects.get(id=upload_obj.id)
    #     assert not upload_obj.validation.is_valid

    #     validate_data(upload_obj.id, model="Upload")
    #     upload_obj = Upload.objects.get(id=upload_obj.id)
    #     assert upload_obj.validation.is_valid

    def test_unregistered_model(self, url_obj):
        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.validation.is_valid is None

        validate_data(url_obj.id, model="SomeNew")
        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.validation.is_valid is None

    def test_not_json_file(self, upload_obj):
        with open(upload_obj.file.path, "w") as f:
            f.write("some txt file")

        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert not upload_obj.validation.is_valid

        validate_data(upload_obj.id, model="Upload")
        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert not upload_obj.validation.is_valid

    def test_not_found(self, mocker):
        mocked_logger = mocker.patch("core.tasks.logger")
        obj_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        model = "Upload"
        validate_data(obj_id, model=model)
        mocked_logger.info.assert_called_once_with(
            "Datasource %s %s not found" % (self.model, obj_id),
            extra={
                "MESSAGE_ID": "datasource_not_found",
                "MODEL": model,
                "DATASOURCE_ID": obj_id,
                "TASK": "validate_data",
            },
        )

    def test_handle_exception(self, upload_obj, mocker):
        mocked_logger = mocker.patch("core.tasks.logger")
        mocked_open = mocker.patch("core.tasks.open")
        mocked_open.side_effect = Exception("Open fails")
        validate_data(upload_obj.id, model=self.model)
        assert mocked_logger.exception.call_count == 1
        datasource = Upload.objects.get(id=upload_obj.id)
        assert not datasource.validation.is_valid
        assert datasource.validation.errors == f"Error while validating data `{str(mocked_open.side_effect)}`"

    def test_no_left_space(self, upload_obj, mocker):
        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert upload_obj.validation.is_valid is None
        assert not upload_obj.available_tables

        mocked_dumps = mocker.patch("core.tasks.json.dumps")
        mocked_dumps.side_effect = OSError(errno.ENOSPC, "No left space.")
        validate_data(upload_obj.id, model="Upload")

        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert not upload_obj.validation.is_valid
        assert upload_obj.validation.errors == "Currently, the space limit was reached. Please try again later."


@pytest.mark.django_db
class TestCleanupUploadTask(BaseUploadTestSuite):
    def test_success(self, upload_obj):
        expired_at = timezone.now()
        upload_obj.expired_at = expired_at
        upload_obj.save(update_fields=["expired_at"])
        assert not upload_obj.deleted

        cleanup_upload(upload_obj.id, model=self.model)
        with pytest.raises(Upload.DoesNotExist):
            Upload.objects.get(id=upload_obj.id)

    def test_skip_cleanup(self, upload_obj):
        expired_at = timezone.now() + timedelta(minutes=1)
        upload_obj.expired_at = expired_at
        upload_obj.save(update_fields=["expired_at"])
        assert not upload_obj.deleted

        cleanup_upload(upload_obj.id, model=self.model)
        upload_obj = Upload.objects.get(id=upload_obj.id)
        assert not upload_obj.deleted

    def test_unregistered_model(self, upload_obj, mocker):
        shutil = mocker.patch("core.tasks.shutil")
        cleanup_upload(upload_obj.id, model="SomeNew")
        assert shutil.rmtree.call_count == 0

    def test_cleanup_not_found(self, mocker):
        mocked_logger = mocker.patch("core.tasks.logger")
        obj_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        cleanup_upload(obj_id, model=self.model)
        mocked_logger.info.assert_called_once_with(
            "Datasource %s %s not found" % (self.model, obj_id),
            extra={
                "MESSAGE_ID": "datasource_not_found",
                "MODEL": self.model,
                "DATASOURCE_ID": obj_id,
                "TASK": "cleanup_upload",
            },
        )


@pytest.mark.django_db
class TestDownloadDataSource:
    model = "Url"

    def test_success(self, mocked_request, url_obj, dataset):
        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == Url.QUEUED_DOWNLOAD
        assert not url_obj.downloaded

        download_data_source(url_obj.id, model=self.model)
        url_obj = Url.objects.get(id=url_obj.id)

        assert url_obj.status == Url.QUEUED_VALIDATION
        assert url_obj.downloaded

        test_dataset = json.loads(dataset.read())
        with open(url_obj.file.path) as f:
            data = json.loads(f.read())
        assert data == test_dataset

        with open(url_obj.analyzed_file.path) as f:
            data = json.loads(f.read())
        assert data == test_dataset

    def test_unregistered_model(self, mocked_request, url_obj):
        download_data_source(url_obj.id, model="SomeNew")

        assert mocked_request.get.call_count == 0

    def test_fail_request_on_data_download(self, mocked_request, url_obj):
        response = Response(status_code=403)
        mocked_request.get.side_effect = [response]

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == Url.QUEUED_DOWNLOAD
        assert not url_obj.downloaded
        download_data_source(url_obj.id, model=self.model)

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "failed"
        assert url_obj.error == f"{response.status_code}: {response.reason}"
        assert mocked_request.get.call_count == 1

    def test_fail_request_on_analyzed_data_download(self, mocked_request, url_obj, dataset):
        response = Response(status_code=403)
        success_response = mocked_request.get.return_value
        mocked_request.get.side_effect = [success_response, response]

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == Url.QUEUED_DOWNLOAD
        assert not url_obj.downloaded
        download_data_source(url_obj.id, model=self.model)

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "failed"
        assert url_obj.error == f"{response.status_code}: {response.reason}"
        assert mocked_request.get.call_count == 2

        with open(url_obj.file.path) as f:
            data = json.loads(f.read())
        assert data == json.loads(dataset.read())

    def test_exception_on_analyzed_data_download(self, mocked_request, url_obj, dataset):
        success_response = mocked_request.get.return_value
        mocked_request.get.side_effect = [success_response, Exception("Some error from remote host")]

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == Url.QUEUED_DOWNLOAD
        assert not url_obj.downloaded
        download_data_source(url_obj.id, model=self.model)

        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == "failed"
        assert url_obj.error == "Something went wrong. Contact with support service."
        assert mocked_request.get.call_count == 2

        with open(url_obj.file.path) as f:
            data = json.loads(f.read())
        assert data == json.loads(dataset.read())

    def test_not_found(self, mocker):
        mocked_logger = mocker.patch("core.tasks.logger")
        obj_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        download_data_source(obj_id, model=self.model)
        mocked_logger.info.assert_called_once_with(
            "Datasource %s %s not found" % (self.model, obj_id),
            extra={
                "MESSAGE_ID": "datasource_not_found",
                "MODEL": self.model,
                "DATASOURCE_ID": obj_id,
                "TASK": "download_data_source",
            },
        )

    def test_no_left_space(self, mocked_request, url_obj, dataset, mocker):
        url_obj = Url.objects.get(id=url_obj.id)
        assert url_obj.status == Url.QUEUED_DOWNLOAD
        assert not url_obj.downloaded

        mocked_request.get.return_value.iter_content = mocker.MagicMock()
        mocked_request.get.return_value.iter_content.side_effect = OSError(errno.ENOSPC, "No left space.")

        download_data_source(url_obj.id, model=self.model)
        url_obj = Url.objects.get(id=url_obj.id)

        assert url_obj.status == Url.FAILED
        assert url_obj.error == "Currently, the space limit was reached. Please try again later."


@pytest.mark.django_db
class TestFlattenDataTask:
    model = "Upload"
    url_prefix = url_prefix = "/uploads/" if not settings.API_PREFIX else f"/{settings.API_PREFIX}uploads/"

    def test_flatten_non_registered_model(self, client, upload_obj_validated, mocker):
        _, flatten_id = create_flatten(client, upload_obj_validated, self.url_prefix)
        model = "NewModel"
        mocked_logger = mocker.patch("core.tasks.logger")
        flatten_data(flatten_id, model=model)

        mocked_logger.info.assert_called_once_with(
            "Model %s not registered in getters" % model,
            extra={
                "MESSAGE_ID": "model_not_registered",
                "MODEL": model,
                "TASK": "flatten_data",
                "FLATTEN_ID": flatten_id,
            },
        )

    def test_flatten_not_found(self, mocker):
        mocked_logger = mocker.patch("core.tasks.logger")
        flatten_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        flatten_data(flatten_id, model=self.model)
        mocked_logger.info.assert_called_once_with(
            "Flatten %s for %s model not found" % (flatten_id, self.model),
            extra={
                "MESSAGE_ID": "flatten_not_found",
                "MODEL": self.model,
                "FLATTEN_ID": flatten_id,
                "TASK": "flatten_data",
            },
        )

    def test_flatten_handle_type_error(self, client, upload_obj_validated, mocker):
        _, flatten_id = create_flatten(client, upload_obj_validated, self.url_prefix)
        mocked_get_options = mocker.patch("core.tasks.get_flatten_options")
        exc_message = "TypeError message"
        mocked_get_options.side_effect = TypeError(exc_message)
        flatten_data(flatten_id, model=self.model)

        flatten = Flatten.objects.get(id=flatten_id)
        assert flatten.status == Flatten.FAILED
        assert flatten.error == exc_message

    def test_flatten_xlsx_successful(self, client, upload_obj_validated):
        _, flatten_id = create_flatten(client, upload_obj_validated, self.url_prefix)
        flatten_data(flatten_id, model=self.model)

        flatten = Flatten.objects.get(id=flatten_id)
        assert flatten.status == Flatten.COMPLETED
        assert flatten.file.path.startswith(settings.MEDIA_ROOT)
        assert flatten.file.path.endswith(Flatten.XLSX)

    def test_flatten_csv_successful(self, client, upload_obj_validated):
        selection_id, flatten_id = create_flatten(
            client, upload_obj_validated, prefix=self.url_prefix, export_format=Flatten.CSV
        )
        selection = DataSelection.objects.get(id=selection_id)
        table1 = selection.tables.all()[0]
        table1.split = True
        table1.heading = "New Table Name"
        table1.save(update_fields=["split", "heading"])

        table2 = selection.tables.all()[1]
        table2.include = False
        table2.save(update_fields=["include"])

        flatten_data(flatten_id, model=self.model)

        flatten = Flatten.objects.get(id=flatten_id)
        assert flatten.status == Flatten.COMPLETED
        assert flatten.file.path.startswith(settings.MEDIA_ROOT)
        assert flatten.file.path.endswith(".zip")

    def test_no_left_space(self, client, upload_obj_validated, mocker):
        _, flatten_id = create_flatten(client, upload_obj_validated, self.url_prefix)
        mocked_flattener = mocker.patch("core.tasks.FileFlattener.flatten_file")
        mocked_flattener.side_effect = OSError(errno.ENOSPC, "No left space.")
        flatten_data(flatten_id, model=self.model)

        flatten = Flatten.objects.get(id=flatten_id)
        assert flatten.status == Flatten.FAILED
        assert flatten.error == "Currently, the space limit was reached. Please try again later."

    def test_flatten_csv_successful_lite(self, client, upload_obj_validated):
        selection_id, flatten_id = create_flatten(
            client, upload_obj_validated, prefix=self.url_prefix, export_format=Flatten.CSV, kind="ocds_lite"
        )
        selection = DataSelection.objects.get(id=selection_id)
        assert selection.kind == selection.OCDS_LITE
        assert selection.headings_type == selection.EN_USER_FRIENDLY
        tables = selection.tables.all()
        assert len(tables) == 3

        flatten_data(flatten_id, model=self.model)

        flatten = Flatten.objects.get(id=flatten_id)
        assert flatten.status == Flatten.COMPLETED
        assert flatten.file.path.startswith(settings.MEDIA_ROOT)
        assert flatten.file.path.endswith(".zip")

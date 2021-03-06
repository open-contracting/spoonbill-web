import shutil

import pytest
from django.conf import settings
from rest_framework import status

from core.models import DataSelection, Flatten, Upload
from core.serializers import UploadSerializer
from core.tests.utils import create_data_selection, create_flatten, get_data_selections


@pytest.mark.django_db
class TestUpload:
    url_prefix = "/uploads/" if not settings.API_PREFIX else f"/{settings.API_PREFIX}uploads/"

    def test_create_upload_wo_file(self, client):
        response = client.post(self.url_prefix, {"attr": "value"})
        assert response.status_code == 400
        assert response.json() == {"detail": "File is required"}

    def test_create_upload_successful(self, client, dataset, cleanup_upload_task, validation_task):
        response = client.post(self.url_prefix, {"file": dataset})
        assert response.status_code == 201
        upload = response.json()
        assert set(upload.keys()) == {
            "analyzed_file",
            "available_tables",
            "created_at",
            "deleted",
            "expired_at",
            "file",
            "id",
            "root_key",
            "selections",
            "status",
            "unavailable_tables",
            "validation",
        }
        assert set(upload["validation"].keys()) == {"id", "task_id", "is_valid", "errors"}
        assert upload["file"].startswith(settings.MEDIA_URL)
        assert not upload["deleted"]

        upload_obj = Upload.objects.get(id=upload["id"])
        validation_task.delay.assert_called_once_with(upload_obj.id, model="Upload", lang_code="en")
        cleanup_upload_task.apply_async.assert_called_once_with(
            (upload_obj.id, "Upload", "en"), eta=upload_obj.expired_at
        )

        # cleanup test data
        shutil.rmtree(f"{settings.MEDIA_ROOT}{upload_obj.id}")

    def test_get_non_existed_upload(self, client):
        response = client.get(f"{self.url_prefix}some-invalid-id/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_get_upload_successful(self, client, upload_obj):
        response = client.get(f"{self.url_prefix}{upload_obj.id}/")
        assert response.status_code == 200
        assert UploadSerializer(upload_obj).data == response.json()

    def test_create_selections_successful(self, client, upload_obj):
        create_data_selection(client, upload_obj, self.url_prefix)

    def test_create_selections_failed(self, client, upload_obj):
        url = f"{self.url_prefix}{upload_obj.id}/selections/"
        data = {"tables": "name"}
        response = client.post(url, content_type="application/json", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": {"tables": {"non_field_errors": ['Expected a list of items but got type "str".']}}
        }

        data = {"tables": []}
        response = client.post(url, content_type="application/json", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": {"tables": {"non_field_errors": ["This list may not be empty."]}}}

    def test_get_selections_successful(self, client, upload_obj):
        get_data_selections(client, upload_obj, self.url_prefix)

    def test_delete_table(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        response = client.get(f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

        table_data = response.json()[0]
        assert table_data["include"]

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{table_data['id']}/",
            content_type="application/json",
            data={"include": False},
        )
        assert response.status_code == 200
        assert not response.json()["include"]

        response = client.get(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{table_data['id']}/"
        )
        assert not response.json()["include"]

    def test_list_tables(self, client, upload_obj):
        selection = create_data_selection(client, upload_obj, self.url_prefix)
        response = client.get(f"{self.url_prefix}{upload_obj.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

    def test_table_preview(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/").json()

        response = client.get(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading"}

    def test_table_r_friendly_preview(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/").json()
        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )

        response = client.get(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "column_headings", "heading"}

    def test_table_split_preview(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.get(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 4
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading", "column_headings"}

    def test_table_split_include_preview(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == 200
        array_tables = response.json()["array_tables"]

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{array_tables[0]['id']}/",
            data={"include": False},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.get(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 3
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading", "column_headings"}

    def test_flatten_create_successful(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        file_formats = ("xlsx", "csv")
        for file_format in file_formats:
            response = client.post(
                f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/flattens/",
                content_type="application/json",
                data={"export_format": file_format},
            )
            assert response.status_code == 201
            flatten_id = response.json()["id"]
            response = client.get(
                f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/flattens/{flatten_id}/",
            )
            flatten_data = response.json()
            assert set(flatten_data.keys()) == {"id", "export_format", "file", "status", "error"}
            assert flatten_data["export_format"] == file_format
            assert flatten_data["file"] is None
            assert flatten_data["status"] == "scheduled"
            assert flatten_data["error"] == ""

    def test_flatten_create_duplicate_fail(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        file_format = "xlsx"
        response = client.post(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/flattens/",
            content_type="application/json",
            data={"export_format": file_format},
        )
        assert response.status_code == 201
        flatten_data = response.json()
        assert set(flatten_data.keys()) == {"id", "export_format", "file", "status", "error"}
        assert flatten_data["export_format"] == file_format
        assert flatten_data["file"] is None
        assert flatten_data["status"] == "scheduled"
        assert flatten_data["error"] == ""

        response = client.post(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/flattens/",
            content_type="application/json",
            data={"export_format": file_format},
        )
        response_data = response.json()
        assert response.status_code == 400
        assert response_data == {"detail": "Flatten request for this type already exists."}

    def test_flatten_create_fail(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        response = client.post(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection['id']}/flattens/",
            content_type="application/json",
            data={"export_format": "file_format"},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": {"export_format": ['"file_format" is not a valid choice.']}}

    def test_flatten_update_fail(self, client, upload_obj_validated):
        selection_id, flatten_id = create_flatten(client, upload_obj_validated, self.url_prefix)
        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection_id}/flattens/{flatten_id}/",
            content_type="application/json",
            data={"status": "hurry-up"},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": f"You can't reschedule flatten in ({Flatten.SCHEDULED}) status"}

        # set flatten terminated status
        flatten = Flatten.objects.get(id=flatten_id)
        flatten.status = Flatten.COMPLETED
        flatten.save(update_fields=["status"])

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection_id}/flattens/{flatten_id}/",
            content_type="application/json",
            data={"status": Flatten.PROCESSING},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": f"You can set status to {Flatten.SCHEDULED} only"}

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection_id}/flattens/{flatten_id}/",
            content_type="application/json",
            data={"status": Flatten.PROCESSING, "export_format": "file_format"},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": {"export_format": ['"file_format" is not a valid choice.']}}

    def test_list_flattens(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, self.url_prefix)
        selection_id = selection["id"]
        url = f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection_id}/flattens/"
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() == []

        _selection_id, flatten_id = create_flatten(client, upload_obj_validated, self.url_prefix, selection_id)
        assert selection_id == _selection_id
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == flatten_id

    def test_flatten_update_successful(self, client, upload_obj_validated):
        selection_id, flatten_id = create_flatten(client, upload_obj_validated, self.url_prefix)
        flatten = Flatten.objects.get(id=flatten_id)
        flatten.status = Flatten.COMPLETED
        flatten.save(update_fields=["status"])

        response = client.get(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection_id}/flattens/{flatten_id}/"
        )
        assert response.status_code == 200
        assert response.json()["status"] == Flatten.COMPLETED

        response = client.patch(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection_id}/flattens/{flatten_id}/",
            content_type="application/json",
            data={"status": Flatten.SCHEDULED},
        )
        assert response.status_code == 200
        response = client.get(
            f"{self.url_prefix}{upload_obj_validated.id}/selections/{selection_id}/flattens/{flatten_id}/"
        )
        assert response.status_code == 200
        assert response.json()["status"] == Flatten.SCHEDULED

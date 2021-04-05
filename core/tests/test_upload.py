import shutil

import pytest
from django.conf import settings

from core.models import Upload
from core.serializers import UploadSerializer
from core.tests.utils import create_data_selection, get_data_selections


@pytest.mark.django_db
class TestUpload:
    def test_create_upload_wo_file(self, client):
        response = client.post("/uploads/", {"attr": "value"})
        assert response.status_code == 400
        assert response.json() == {"detail": "File is required"}

    def test_create_upload_successful(self, client, dataset, cleanup_upload_task, validation_task):
        response = client.post("/uploads/", {"file": dataset})
        assert response.status_code == 201
        upload = response.json()
        assert set(upload.keys()) == {
            "available_tables",
            "expired_at",
            "id",
            "deleted",
            "validation",
            "created_at",
            "file",
            "status",
            "selections",
        }
        assert set(upload["validation"].keys()) == {"id", "task_id", "is_valid", "errors"}
        assert upload["file"].startswith(settings.MEDIA_URL)
        assert not upload["deleted"]

        upload_obj = Upload.objects.get(id=upload["id"])
        validation_task.delay.assert_called_once_with(upload_obj.id, model="Upload")
        cleanup_upload_task.apply_async.assert_called_once_with((upload_obj.id, "Upload"), eta=upload_obj.expired_at)

        # cleanup test data
        shutil.rmtree(f"{settings.MEDIA_ROOT}{upload_obj.id}")

    def test_get_non_existed_upload(self, client):
        response = client.get("/uploads/some-invalid-id/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_get_upload_successful(self, client, upload_obj):
        response = client.get(f"/uploads/{upload_obj.id}/")
        assert response.status_code == 200
        assert UploadSerializer(upload_obj).data == response.json()

    def test_create_selections_successful(self, client, upload_obj):
        create_data_selection(client, upload_obj, "uploads")

    def test_get_selections_successful(self, client, upload_obj):
        get_data_selections(client, upload_obj, "uploads")

    def test_delete_table(self, client, upload_obj):
        selection = create_data_selection(client, upload_obj, "uploads")
        response = client.get(f"/uploads/{upload_obj.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

        table_data = response.json()[0]
        assert table_data["include"]

        response = client.patch(
            f"/uploads/{upload_obj.id}/selections/{selection['id']}/tables/{table_data['id']}/",
            content_type="application/json",
            data={"include": False},
        )
        assert response.status_code == 200
        assert not response.json()["include"]

        response = client.get(f"/uploads/{upload_obj.id}/selections/{selection['id']}/tables/{table_data['id']}/")
        assert not response.json()["include"]

    def test_list_tables(self, client, upload_obj):
        selection = create_data_selection(client, upload_obj, "uploads")
        response = client.get(f"/uploads/{upload_obj.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

    def test_table_preview(self, client, upload_obj):
        selection = create_data_selection(client, upload_obj, "uploads")
        tables = client.get(f"/uploads/{upload_obj.id}/selections/{selection['id']}/tables/").json()

        response = client.get(
            f"/uploads/{upload_obj.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview"}

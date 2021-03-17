import pytest

from core.models import Url
from core.serializers import UrlSerializer


@pytest.mark.django_db
class TestUrl:
    def test_create_datasource_wo_url(self, client):
        response = client.post("/urls/", {"attr": "value"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Url is required"}

    def test_create_datasource_successful(self, client, download_datasource_task):
        response = client.post("/urls/", {"url": "https://example.org/dataset.json"})
        assert response.status_code == 201
        url = response.json()
        assert set(url.keys()) == {
            "analyzed_data_filename",
            "analyzed_data_url",
            "created_at",
            "deleted",
            "downloaded",
            "error",
            "expired_at",
            "filename",
            "id",
            "status",
            "url",
            "validation",
        }
        assert set(url["validation"].keys()) == {"id", "task_id", "is_valid", "errors"}
        assert not url["deleted"]
        assert url["status"] == "queued.download"

        url_obj = Url.objects.get(id=url["id"])
        download_datasource_task.delay.assert_called_once_with(url_obj.id, model="Url")

    def test_get_non_existed_datasource(self, client):
        response = client.get("/urls/some-invalid-id/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_get_url_successful(self, client, url_obj):
        response = client.get(f"/urls/{url_obj.id}/")
        assert response.status_code == 200
        assert UrlSerializer(url_obj).data == response.json()

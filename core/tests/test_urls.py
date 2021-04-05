import pytest

from core.models import Url
from core.serializers import UrlSerializer

from .utils import create_data_selection, get_data_selections


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
            "analyzed_data_url",
            "analyzed_file",
            "available_tables",
            "created_at",
            "selections",
            "deleted",
            "downloaded",
            "error",
            "expired_at",
            "file",
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

    def test_create_selections_successful(self, client, url_obj):
        create_data_selection(client, url_obj, prefix="urls")

    def test_get_selections_successful(self, client, url_obj):
        get_data_selections(client, url_obj, "urls")

    def test_delete_table(self, client, url_obj):
        selection = create_data_selection(client, url_obj, "urls")
        response = client.get(f"/urls/{url_obj.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

        table_data = response.json()[0]
        assert table_data["include"]

        response = client.patch(
            f"/urls/{url_obj.id}/selections/{selection['id']}/tables/{table_data['id']}/",
            content_type="application/json",
            data={"include": False},
        )
        assert response.status_code == 200
        assert not response.json()["include"]

        response = client.get(f"/urls/{url_obj.id}/selections/{selection['id']}/tables/{table_data['id']}/")
        assert not response.json()["include"]

    def test_list_tables(self, client, url_obj):
        selection = create_data_selection(client, url_obj, "urls")
        response = client.get(f"/urls/{url_obj.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

    def test_table_preview(self, client, url_obj):
        selection = create_data_selection(client, url_obj, "urls")
        tables = client.get(f"/urls/{url_obj.id}/selections/{selection['id']}/tables/").json()

        response = client.get(f"/urls/{url_obj.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/")
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"name", "preview"}

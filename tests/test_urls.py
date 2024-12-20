import json
import os
import pathlib
import shutil
from base64 import b64encode

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from spoonbill_web.models import Url
from spoonbill_web.serializers import UrlSerializer
from spoonbill_web.utils import dataregistry_path_formatter, dataregistry_path_resolver
from tests import ANALYZED_DATA_PATH, create_data_selection, get_data_selections

DATA_DIR = os.path.dirname(__file__) + "/data"
DATASET_PATH = f"{DATA_DIR}/sample-dataset.json"


@pytest.mark.django_db
class TestUrl:
    def test_create_datasource_wo_url(self, client):
        response = client.post("/api/urls/", {"attr": "value"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Url is required"}

    def test_create_datasource_successful(self, client, download_datasource_task):
        response = client.post("/api/urls/", {"urls": ["https://example.org/dataset.json"]})
        assert response.status_code == 201
        url = response.json()
        assert set(url.keys()) == {
            "analyzed_data_url",
            "analyzed_file",
            "available_tables",
            "created_at",
            "deleted",
            "downloaded",
            "error",
            "expired_at",
            "files",
            "id",
            "root_key",
            "selections",
            "status",
            "unavailable_tables",
            "urls",
            "validation",
            "source",
            "period",
            "country",
            "order",
            "author",
        }
        assert set(url["validation"].keys()) == {"id", "task_id", "is_valid", "errors"}
        assert not url["deleted"]
        assert url["status"] == "queued.download"
        assert url["country"] == ""
        assert url["period"] == ""
        assert url["source"] == ""

        url_obj = Url.objects.get(id=url["id"])

        download_datasource_task.delay.assert_called_once_with(url_obj.id, model="Url", lang_code="en-us")

        response = client.post(
            "/api/urls/",
            {
                "urls": "https://example.org/dataset.json",
                "country": "Mordor",
                "period": "I was there, Gandalf, three thousands years ago",
                "source": "Elrond",
            },
        )
        assert response.status_code == 201
        url = response.json()
        assert url["country"] == "Mordor"
        assert url["period"] == "I was there, Gandalf, three thousands years ago"
        assert url["source"] == "Elrond"

    def test_get_non_existed_datasource(self, client):
        response = client.get("/api/urls/some-invalid-id/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_get_url_successful(self, client, url_obj):
        response = client.get(f"/api/urls/{url_obj.id}/")
        assert response.status_code == 200
        assert UrlSerializer(url_obj).data == response.json()

    def test_create_selections_successful(self, client, url_obj):
        with open(ANALYZED_DATA_PATH, "rb") as af:
            url_obj.analyzed_file.save("new", af)
        create_data_selection(client, url_obj, prefix="/api/urls/")

    def test_get_selections_successful(self, client, url_obj):
        with open(ANALYZED_DATA_PATH, "rb") as af:
            url_obj.analyzed_file.save("new", af)
        get_data_selections(client, url_obj, "/api/urls/")

    def test_delete_table(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, "/api/urls/")
        response = client.get(f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

        table_data = response.json()[0]
        assert table_data["include"]

        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{table_data['id']}/",
            content_type="application/json",
            data={"include": False},
        )
        assert response.status_code == 200
        assert not response.json()["include"]

        response = client.get(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{table_data['id']}/"
        )
        assert not response.json()["include"]

    def test_list_tables(self, client, url_obj):
        with open(ANALYZED_DATA_PATH, "rb") as af:
            url_obj.analyzed_file.save("new", af)
        selection = create_data_selection(client, url_obj, "/api/urls/")
        response = client.get(f"/api/urls/{url_obj.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

    def test_table_preview(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, "/api/urls/")
        tables = client.get(f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.get(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading", "should_split", "parent", "include"}

    def test_table_r_friendly_preview(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, "/api/urls/")
        tables = client.get(f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()
        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )

        response = client.get(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {
            "id",
            "name",
            "preview",
            "heading",
            "column_headings",
            "should_split",
            "parent",
            "include",
        }

    def test_table_split_preview(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, "/api/urls/")
        tables = client.get(f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.get(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )

        assert len(response.json()) == 4
        data = response.json()[0]
        assert set(data.keys()) == {
            "id",
            "name",
            "preview",
            "heading",
            "column_headings",
            "should_split",
            "parent",
            "include",
        }

    def test_table_split_include_preview(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, "/api/urls/")
        tables = client.get(f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == 200
        array_tables = response.json()["array_tables"]

        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{array_tables[0]['id']}/",
            data={"include": False},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.get(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 4
        data = response.json()[0]
        assert set(data.keys()) == {
            "id",
            "name",
            "preview",
            "heading",
            "column_headings",
            "should_split",
            "parent",
            "include",
        }

    def test_table_split_failed(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, "/api/urls/")
        tables = client.get(f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"/api/urls/{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_dataregistry_path(self, client, tmp_path):
        with override_settings(DATAREGISTRY_MEDIA_ROOT=pathlib.Path(str(tmp_path) + "/data_registry")):
            file = tmp_path / "data_registry/file.json"
            file.parent.mkdir()
            file.touch()
            username = "test"
            password = "test"
            user = User.objects.create_user(username=username, password=password)
            user.save()
            credentials = f"{username}:{password}"
            encoded_credentials = b64encode(credentials.encode("ascii")).decode("ascii")

            # Relative path
            url = "file://file.json"
            response = client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert os.path.isfile(file)
            assert str(path) == str(file)
            assert response.status_code == 201

            # No login
            response = client.post("/api/urls/", {"urls": url})
            assert response.status_code == 403

            # Absolute path
            url = "file://" + str(file)
            response = client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert str(path) == str(file)
            assert response.status_code == 201

            # Path outside of data registry folder
            forbidden_file = tmp_path / "forbidden_file.json"
            forbidden_file.touch()
            url = "file://" + str(tmp_path) + "/forbidden_file.json"
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert str(path) == str(forbidden_file)
            assert os.path.isfile(forbidden_file)
            with pytest.raises(ValueError) as e:
                client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            assert "Input URL is invalid" in str(e)

            # Path that leads outside of data registry folder
            url = "file://" + str(tmp_path) + "/data_registry/../forbidden_file.json"
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert str(path) == str(tmp_path) + "/forbidden_file.json"
            with pytest.raises(ValueError) as e:
                client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            assert "Input URL is invalid" in str(e)

            # Path that leads to root
            url = "file:///./../../../../../../../../forbidden_file.json"
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert str(path) == "/forbidden_file.json"
            with pytest.raises(ValueError) as e:
                client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")

            # Symlink not allowed
            dest = tmp_path / "data_registry/forbidden_file.json"
            os.symlink(forbidden_file, str(dest))
            assert os.path.islink(dest)
            url = "file://" + str(tmp_path) + "/data_registry" + "/forbidden_file.json"
            with pytest.raises(ValueError) as e:
                client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            assert "Input URL is invalid" in str(e)

            # Symlink allowed, jail is on
            with override_settings(DATAREGISTRY_ALLOW_SYMLINKS=True), pytest.raises(ValueError) as e:
                client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
                assert "Input URL is invalid" in str(e)

            # Symlink allowed, jail is off
            with override_settings(DATAREGISTRY_ALLOW_SYMLINKS=True, DATAREGISTRY_JAIL=False):
                client.post("/api/urls/", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
                assert response.status_code == 201

            # Multi upload dataregistry path creation successful
            paths = []
            for i in range(1, 6):
                dest = tmp_path / f"data_registry/file{i}.json"
                shutil.copyfile(DATASET_PATH, dest)
                url = f"file://file{i}.json"
                paths.append(url)
                assert os.path.isfile(dest)

            response = client.post(
                "/api/urls/",
                json.dumps({"urls": paths}),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Basic {encoded_credentials}",
            )
            url = response.json()
            assert response.status_code == 201
            assert url["urls"] == paths
            assert url["status"] == "queued.download"

            # Multi upload with invalid URL
            paths.append("https://www.google.com/")
            response = client.post(
                "/api/urls/",
                json.dumps({"urls": paths}),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Basic {encoded_credentials}",
            )
            assert "Multiple uploads are not available for this type of URL" in response.json()["detail"]["urls"]

    def test_dataregistry_path_no_dataregistry_imported(self, client):
        with pytest.raises(ValueError) as e:
            client.post("/api/urls/", {"urls": "file:///file.json"})
        assert "Input URL is invalid" in str(e)

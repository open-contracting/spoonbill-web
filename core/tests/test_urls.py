import json
import os
import pathlib
import shutil
from base64 import b64encode
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings

from core.models import Url
from core.serializers import UrlSerializer
from core.utils import dataregistry_path_formatter, dataregistry_path_resolver

from .conftest import ANALYZED_DATA_PATH
from .utils import create_data_selection, get_data_selections

DATA_DIR = os.path.dirname(__file__) + "/data"
DATASET_PATH = f"{DATA_DIR}/sample-dataset.json"


@pytest.mark.django_db
class TestUrl:
    url_prefix = "/urls/" if not settings.API_PREFIX else f"/{settings.API_PREFIX}urls/"

    def test_create_datasource_wo_url(self, client):
        response = client.post(f"{self.url_prefix}", {"attr": "value"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Url is required"}

    def test_create_datasource_successful(self, client, download_datasource_task):
        response = client.post(f"{self.url_prefix}", {"urls": ["https://example.org/dataset.json"]})
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
        assert url["country"] is None
        assert url["period"] is None
        assert url["source"] is None

        url_obj = Url.objects.get(id=url["id"])

        download_datasource_task.delay.assert_called_once_with(url_obj.id, model="Url", lang_code="en-us")

        response = client.post(
            f"{self.url_prefix}",
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
        response = client.get(f"{self.url_prefix}some-invalid-id/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_get_url_successful(self, client, url_obj):
        response = client.get(f"{self.url_prefix}{url_obj.id}/")
        assert response.status_code == 200
        assert UrlSerializer(url_obj).data == response.json()

    def test_create_selections_successful(self, client, url_obj):
        with open(ANALYZED_DATA_PATH, "rb") as af:
            url_obj.analyzed_file.save("new", af)
        create_data_selection(client, url_obj, prefix=self.url_prefix)

    def test_get_selections_successful(self, client, url_obj):
        with open(ANALYZED_DATA_PATH, "rb") as af:
            url_obj.analyzed_file.save("new", af)
        get_data_selections(client, url_obj, self.url_prefix)

    def test_delete_table(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, self.url_prefix)
        response = client.get(f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

        table_data = response.json()[0]
        assert table_data["include"]

        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{table_data['id']}/",
            content_type="application/json",
            data={"include": False},
        )
        assert response.status_code == 200
        assert not response.json()["include"]

        response = client.get(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{table_data['id']}/"
        )
        assert not response.json()["include"]

    def test_list_tables(self, client, url_obj):
        with open(ANALYZED_DATA_PATH, "rb") as af:
            url_obj.analyzed_file.save("new", af)
        selection = create_data_selection(client, url_obj, self.url_prefix)
        response = client.get(f"{self.url_prefix}{url_obj.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

    def test_table_preview(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.get(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading", "should_split", "parent", "include"}

    def test_table_r_friendly_preview(self, client, url_obj_w_files):
        selection = create_data_selection(client, url_obj_w_files, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()
        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )

        response = client.get(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
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
        selection = create_data_selection(client, url_obj_w_files, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.get(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
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
        selection = create_data_selection(client, url_obj_w_files, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == 200
        array_tables = response.json()["array_tables"]

        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{array_tables[0]['id']}/",
            data={"include": False},
            content_type="application/json",
        )
        assert response.status_code == 200

        response = client.get(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
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
        selection = create_data_selection(client, url_obj_w_files, self.url_prefix)
        tables = client.get(f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/").json()

        response = client.patch(
            f"{self.url_prefix}{url_obj_w_files.id}/selections/{selection['id']}/tables/{tables[0]['id']}",
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
            response = client.post(
                f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}"
            )
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert os.path.isfile(file)
            assert str(path) == str(file)
            assert response.status_code == 201

            # No login
            response = client.post(f"{self.url_prefix}", {"urls": url})
            assert response.status_code == 403

            # Absolute path
            url = "file://" + str(file)
            response = client.post(
                f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}"
            )
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
                client.post(f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            assert "Input URL is invalid" in str(e)

            # Path that leads outside of data registry folder
            url = "file://" + str(tmp_path) + "/data_registry/../forbidden_file.json"
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert str(path) == str(tmp_path) + "/forbidden_file.json"
            with pytest.raises(ValueError) as e:
                client.post(f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            assert "Input URL is invalid" in str(e)

            # Path that leads to root
            url = "file:///./../../../../../../../../forbidden_file.json"
            path = dataregistry_path_resolver(dataregistry_path_formatter(url))
            assert str(path) == "/forbidden_file.json"
            with pytest.raises(ValueError) as e:
                client.post(f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")

            # Symlink not allowed
            dest = tmp_path / "data_registry/forbidden_file.json"
            os.symlink(forbidden_file, str(dest))
            assert os.path.islink(dest)
            url = "file://" + str(tmp_path) + "/data_registry" + "/forbidden_file.json"
            with pytest.raises(ValueError) as e:
                client.post(f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
            assert "Input URL is invalid" in str(e)

            # Symlink allowed, jail is on
            with patch("core.validators.settings.DATAREGISTRY_ALLOW_SYMLINKS", True):
                with pytest.raises(ValueError) as e:
                    client.post(f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
                    assert "Input URL is invalid" in str(e)

            # Symlink allowed, jail is off
            with patch("core.validators.settings.DATAREGISTRY_ALLOW_SYMLINKS", True):
                with patch("core.validators.settings.DATAREGISTRY_JAIL", False):
                    client.post(f"{self.url_prefix}", {"urls": url}, HTTP_AUTHORIZATION=f"Basic {encoded_credentials}")
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
                f"{self.url_prefix}",
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
                f"{self.url_prefix}",
                json.dumps({"urls": paths}),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Basic {encoded_credentials}",
            )
            assert "Multiple uploads are not available for this type of URL" in response.json()["detail"]["urls"]

    def test_dataregistry_path_no_dataregistry_imported(self, client):
        with pytest.raises(ValueError) as e:
            client.post(f"{self.url_prefix}", {"urls": "file:///file.json"})
        assert "Input URL is invalid" in str(e)

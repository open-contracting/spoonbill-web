import errno

import pytest
from django.conf import settings
from rest_framework import status

from core.tests.utils import create_data_selection


@pytest.mark.django_db
class TestTableViews:
    url_prefix = "/uploads/" if not settings.API_PREFIX else f"/{settings.API_PREFIX}uploads/"

    @pytest.fixture(autouse=True)
    def setUp(self, client, dataset, cleanup_upload_task, validation_task, upload_obj, upload_obj_validated, mocker):
        self.client = client
        self.dataset = dataset
        self.task_cleanup = cleanup_upload_task
        self.task_validation = validation_task
        self.datasource = upload_obj
        self.validated_datasource = upload_obj_validated
        self.mocker = mocker

    def test_delete_table(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        )
        assert len(response.json()) == 2

        table_data = response.json()[0]
        assert table_data["include"]

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{table_data['id']}/",
            content_type="application/json",
            data={"include": False},
        )
        assert response.status_code == status.HTTP_200_OK
        assert not response.json()["include"]

        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{table_data['id']}/"
        )
        assert not response.json()["include"]

    def test_list_tables(self):
        selection = create_data_selection(self.client, self.datasource, self.url_prefix)
        response = self.client.get(f"{self.url_prefix}{self.datasource.id}/selections/{selection['id']}/tables/")
        assert len(response.json()) == 2

    def test_table_preview(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()

        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading"}

    def test_table_r_friendly_preview(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()
        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )

        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "column_headings", "heading"}

    def test_table_user_friendly_preview(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()
        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/",
            data={"headings_type": "es_user_friendly"},
            content_type="application/json",
        )

        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 1
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "column_headings", "heading"}

    def test_table_split_preview(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 4
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading", "column_headings"}

    def test_table_split_include_preview(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        array_tables = response.json()["array_tables"]

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{array_tables[0]['id']}/",
            data={"include": False},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert len(response.json()) == 3
        data = response.json()[0]
        assert set(data.keys()) == {"id", "name", "preview", "heading", "column_headings"}

    def test_table_split_no_left_space(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()
        mocked_split = self.mocker.patch("core.views.store_preview_csv")
        mocked_split.side_effect = OSError(errno.ENOSPC, "No left space.")

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert response.json() == {"detail": "Currently, the space limit was reached. Please try again later."}

    def test_table_split_preview_no_left_space(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        array_tables = response.json()["array_tables"]

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/",
            data={"headings_type": "es_r_friendly"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{array_tables[0]['id']}/",
            data={"include": False},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        mocked_split = self.mocker.MagicMock()
        mocked_split.side_effect = OSError(errno.ENOSPC, "No left space.")
        with self.mocker.patch("core.views.store_preview_csv", mocked_split):
            response = self.client.get(
                f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
            )
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert response.json() == {"detail": "Currently, the space limit was reached. Please try again later."}

    def test_table_split_file_not_found(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()
        mocked_open = self.mocker.patch("core.views.DataPreprocessor.restore")
        mocked_open.side_effect = FileNotFoundError(errno.ENOENT, "File not found.")

        response = self.client.patch(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/",
            data={"split": True},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Datasource expired."}

    def test_table_preview_file_not_found(self):
        selection = create_data_selection(self.client, self.validated_datasource, self.url_prefix)
        tables = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/"
        ).json()

        mocked_open = self.mocker.patch("core.views.open")
        mocked_open.return_value.__enter__.side_effect = FileNotFoundError(errno.ENOENT, "File not found.")

        response = self.client.get(
            f"{self.url_prefix}{self.validated_datasource.id}/selections/{selection['id']}/tables/{tables[0]['id']}/preview/"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Datasource expired."}

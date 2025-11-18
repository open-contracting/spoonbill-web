import pytest

from spoonbill_web.models import Flatten
from tests import create_data_selection, create_flatten


@pytest.mark.django_db
class TestFlattenViews:
    @pytest.fixture(autouse=True)
    def setUp(self, client, upload_obj_validated):
        selection = create_data_selection(client, upload_obj_validated, "/api/uploads/")
        self.selection_id = selection["id"]
        self.flattens_url = f"/api/uploads/{upload_obj_validated.id}/selections/{selection['id']}/flattens/"
        self.datasource = upload_obj_validated
        self.client = client

    def test_flatten_create_successful(self):
        for file_format in ("xlsx", "csv"):
            response = self.client.post(
                self.flattens_url,
                content_type="application/json",
                data={"export_format": file_format},
            )
            assert response.status_code == 201
            flatten_id = response.json()["id"]
            flatten_url = f"{self.flattens_url}{flatten_id}/"
            response = self.client.get(flatten_url)
            flatten_data = response.json()
            assert set(flatten_data.keys()) == {"id", "export_format", "file", "status", "error"}
            assert flatten_data["export_format"] == file_format
            assert flatten_data["file"] is None
            assert flatten_data["status"] == "scheduled"
            assert flatten_data["error"] == ""

    def test_flatten_create_duplicate_fail(self):
        file_format = "xlsx"
        response = self.client.post(
            self.flattens_url,
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

        response = self.client.post(
            self.flattens_url,
            content_type="application/json",
            data={"export_format": file_format},
        )
        response_data = response.json()
        assert response.status_code == 400
        assert response_data == {"detail": "Flatten request for this type already exists."}

    def test_flatten_create_fail(self):
        response = self.client.post(
            self.flattens_url,
            content_type="application/json",
            data={"export_format": "file_format"},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": {"export_format": ['"file_format" is not a valid choice.']}}

    def test_flatten_update_fail(self):
        _, flatten_id = create_flatten(self.client, self.datasource, "/api/uploads/")
        flatten_url = f"{self.flattens_url}{flatten_id}/"
        response = self.client.patch(flatten_url, content_type="application/json", data={"status": "hurry-up"})
        assert response.status_code == 400
        assert response.json() == {"detail": f"You can't reschedule flatten in ({Flatten.SCHEDULED}) status"}

        # set flatten terminated status
        flatten = Flatten.objects.get(id=flatten_id)
        flatten.status = Flatten.COMPLETED
        flatten.save(update_fields=["status"])

        response = self.client.patch(flatten_url, content_type="application/json", data={"status": Flatten.PROCESSING})
        assert response.status_code == 400
        assert response.json() == {"detail": f"You can set status to {Flatten.SCHEDULED} only"}

        response = self.client.patch(
            flatten_url,
            content_type="application/json",
            data={"status": Flatten.PROCESSING, "export_format": "file_format"},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": {"export_format": ['"file_format" is not a valid choice.']}}

    def test_list_flattens(self):
        response = self.client.get(self.flattens_url)
        assert response.status_code == 200
        assert response.json() == []

        selection_id, flatten_id = create_flatten(self.client, self.datasource, "/api/uploads/", self.selection_id)
        assert selection_id == self.selection_id
        response = self.client.get(self.flattens_url)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == flatten_id

    def test_flatten_update_successful(self):
        _, flatten_id = create_flatten(self.client, self.datasource, "/api/uploads/", self.selection_id)
        flatten = Flatten.objects.get(id=flatten_id)
        flatten.status = Flatten.COMPLETED
        flatten.save(update_fields=["status"])

        flatten_url = f"{self.flattens_url}{flatten_id}/"
        response = self.client.get(flatten_url)
        assert response.status_code == 200
        assert response.json()["status"] == Flatten.COMPLETED

        response = self.client.patch(flatten_url, content_type="application/json", data={"status": Flatten.SCHEDULED})
        assert response.status_code == 200
        response = self.client.get(flatten_url)
        assert response.status_code == 200
        assert response.json()["status"] == Flatten.SCHEDULED

    def test_clear_flattens_after_update_dataselection(self):
        selection_id, _ = create_flatten(self.client, self.datasource, "/api/uploads/", self.selection_id)
        response = self.client.get(self.flattens_url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        url = f"/api/uploads/{self.datasource.id}/selections/{selection_id}/"
        response = self.client.patch(url, content_type="application/json", data={"headings_type": "es_r_friendly"})
        assert response.status_code == 200

        response = self.client.get(self.flattens_url)
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_clear_flattens_after_update_table(self):
        selection_id, _ = create_flatten(self.client, self.datasource, "/api/uploads/", self.selection_id)
        response = self.client.get(self.flattens_url)
        assert response.status_code == 200
        assert len(response.json()) == 1

        url = f"/api/uploads/{self.datasource.id}/selections/{selection_id}/"
        response = self.client.get(url)
        assert response.status_code == 200
        selection = response.json()
        table_id = selection["tables"][0]["id"]
        url = f"/api/uploads/{self.datasource.id}/selections/{selection_id}/tables/{table_id}/"

        response = self.client.patch(url, content_type="application/json", data={"heading": "New heading"})
        assert response.status_code == 200

        response = self.client.get(self.flattens_url)
        assert response.status_code == 200
        assert len(response.json()) == 0

import json
import pathlib
import uuid

from spoonbill_web.constants import OCDS_LITE_CONFIG

DATA_DIR = pathlib.Path(__file__).parent / "data"

ANALYZED_DATA_PATH = DATA_DIR / "analyzed.dump"

REASONS = {
    "400": "Bad Request.",
    "401": "401 Unauthorized.",
    "403": "Forbidden.",
    "404": "Not found.",
    "405": "Method Not Allowed.",
}


class Task:
    @property
    def id(self):
        return str(uuid.uuid4())


class Response:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self.headers = {"Content-Length": "204801"}
        self.text = body
        self.url = None

    def iter_content(self, chunk_size=1024):
        binary_body = self.text.encode("utf-8")
        chunk = 0
        while len(binary_body) > chunk:
            yield binary_body[chunk : chunk + chunk_size]
            chunk += chunk_size

    def json(self):
        return json.loads(self.text)

    @property
    def reason(self):
        return REASONS.get(str(self.status_code))


data_selection = {"tables": [{"name": "tenders"}, {"name": "parties"}]}


def create_data_selection(client, parent, prefix=None, kind=None):
    url = f"{prefix}{parent.id}/selections/"
    data = {"kind": kind} if kind and kind == "ocds_lite" else data_selection
    response = client.post(url, content_type="application/json", data=data)
    assert response.status_code == 201
    json_data = response.json()
    assert set(json_data.keys()) == {"id", "tables", "headings_type", "flattens", "kind"}
    if kind:
        assert json_data["kind"] == "ocds_lite"
    else:
        assert json_data["kind"] == "custom"
    if kind and kind == "ocds_lite":
        tables = OCDS_LITE_CONFIG["tables"].keys()
    else:
        tables = [t["name"] for t in data_selection["tables"]]

    assert len(json_data["tables"]) == len(tables)
    for table in json_data["tables"]:
        assert "id" in table
        assert table["name"] in tables
    return json_data


def get_data_selections(client, parent, prefix=None):
    json_data = create_data_selection(client, parent, prefix)

    # get list of selections
    url = f"{prefix}{parent.id}/selections/"
    response = client.get(url)
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp) == 1
    assert json_resp[0] == json_data

    # get single selection by id
    url = f"{prefix}{parent.id}/selections/{json_data['id']}/"
    response = client.get(url)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp == json_data


def create_flatten(client, parent, prefix=None, selection_id=None, export_format="xlsx", kind=None):
    if not selection_id:
        selection = create_data_selection(client, parent, prefix, kind=kind)
        selection_id = selection["id"]

    url = f"{prefix}{parent.id}/selections/{selection_id}/flattens/"
    response = client.post(url, content_type="application/json", data={"export_format": export_format})
    assert response.status_code == 201
    return selection_id, response.json()["id"]

import json
import uuid


class Task:
    @property
    def id(self):
        return str(uuid.uuid4())


class Response:
    reasons = {
        "400": "Bad Request.",
        "401": "401 Unauthorized.",
        "403": "Forbidden.",
        "404": "Not found.",
        "405": "Method Not Allowed.",
    }

    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self.headers = {"Content-Length": "204801"}
        self.text = body
        self.url = None

    def iter_content(self, chunk_size=1024):
        binary_body = self.text.encode("utf-8")
        chunk = 0
        while len(binary_body) > chunk:
            yield binary_body[chunk : chunk + chunk_size]  # noqa
            chunk += chunk_size

    def json(self):
        return json.loads(self.text)

    @property
    def reason(self):
        return self.reasons.get(str(self.status_code))


data_selection = {"tables": [{"name": "parties"}, {"name": "awards"}]}


def create_data_selection(client, parent, prefix=None):
    url = f"{prefix}{parent.id}/selections/"
    response = client.post(url, content_type="application/json", data=data_selection)
    assert response.status_code == 201
    json_data = response.json()
    assert set(json_data.keys()) == {"id", "tables", "headings_type"}
    for i, table in enumerate(json_data["tables"]):
        assert "id" in table
        assert table["name"] == data_selection["tables"][i]["name"]
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

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

import json

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import re_path

from core.consumers import ValidationConsumer
from core.models import Upload, Validation
from core.tasks import download_data_source, validate_data


@pytest.mark.django_db
@pytest.mark.asyncio
class TestValidationConsumer:
    def test_task_validate(self, event_loop):
        validation = Validation.objects.create()
        upload = Upload.objects.create(filename="don.json", validation=validation)

        application = URLRouter([re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", ValidationConsumer.as_asgi())])
        communicator = WebsocketCommunicator(application, f"/ws/api/{upload.id}/")
        event_loop.run_until_complete(communicator.connect())
        validate_data(str(upload.id), model="Upload")
        message = event_loop.run_until_complete(communicator.receive_from())
        event_loop.run_until_complete(communicator.disconnect())

        assert (json.loads(message).keys()) == {"datasource", "type"}

    def test_task_download_data_source(self, event_loop, url_obj, mocked_request):
        application = URLRouter([re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", ValidationConsumer.as_asgi())])
        communicator = WebsocketCommunicator(application, f"/ws/api/{url_obj.id}/")
        event_loop.run_until_complete(communicator.connect())
        download_data_source(str(url_obj.id), model="Url")
        message = event_loop.run_until_complete(communicator.receive_from())
        event_loop.run_until_complete(communicator.disconnect())
        message = json.loads(message)

        assert message["type"] == "task.download_data_source"
        assert message["datasource"]["id"] == str(url_obj.id)
        assert message["datasource"]["status"] == "downloading"
        assert not message["datasource"]["downloaded"]

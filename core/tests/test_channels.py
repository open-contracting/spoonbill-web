import json

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.urls import re_path

from core.consumers import ValidationConsumer
from core.tasks import download_data_source, flatten_data, validate_data

from .utils import create_flatten


@pytest.mark.django_db
@pytest.mark.asyncio
class TestValidationConsumer:
    def test_task_validate(self, event_loop, upload_obj):
        application = URLRouter([re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", ValidationConsumer.as_asgi())])
        communicator = WebsocketCommunicator(application, f"/ws/api/{upload_obj.id}/")
        event_loop.run_until_complete(communicator.connect())
        validate_data(str(upload_obj.id), model="Upload")
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

    def test_task_flatten(self, event_loop, client, upload_obj_validated, mocked_request):
        prefix = "/uploads/" if not settings.API_PREFIX else f"/{settings.API_PREFIX}uploads/"
        _, flatten_id = create_flatten(client, upload_obj_validated, prefix=prefix)
        application = URLRouter([re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", ValidationConsumer.as_asgi())])
        communicator = WebsocketCommunicator(application, f"/ws/api/{upload_obj_validated.id}/")
        event_loop.run_until_complete(communicator.connect())
        flatten_data(flatten_id, model="Upload")
        message = event_loop.run_until_complete(communicator.receive_from())
        event_loop.run_until_complete(communicator.disconnect())
        message = json.loads(message)

        assert message["type"] == "task.flatten"
        assert message["flatten"]["id"] == flatten_id
        assert message["flatten"]["status"] == "processing"

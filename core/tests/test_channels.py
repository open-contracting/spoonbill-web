import json

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import re_path

from core.consumers import ValidationConsumer
from core.models import Upload, Validation
from core.tasks import validate_data


@pytest.mark.django_db
@pytest.mark.asyncio
class TestValidationConsumer:
    def test_success(self, event_loop):
        validation = Validation.objects.create()
        upload = Upload.objects.create(filename="don.json", validation=validation)

        application = URLRouter([re_path(r"ws/api/(?P<upload_id>[0-9a-f-]+)/$", ValidationConsumer.as_asgi())])
        communicator = WebsocketCommunicator(application, f"/ws/api/{upload.id}/")
        event_loop.run_until_complete(communicator.connect())
        validate_data(str(upload.id), str(upload.validation.id))
        message = event_loop.run_until_complete(communicator.receive_from())
        event_loop.run_until_complete(communicator.disconnect())
        assert json.loads(message) == {"message": {"upload_id": str(upload.id), "is_valid": True}}

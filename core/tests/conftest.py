import os
import uuid

import pytest
from django.utils import timezone

from core.models import Upload, Validation


class Task:
    @property
    def id(self):
        return str(uuid.uuid4())


@pytest.fixture
def dataset():
    path = os.path.dirname(__file__) + "/data/don.json"
    file_ = open(path)
    yield file_

    file_.close()


@pytest.fixture
def validation_task(mocker):
    mock = mocker.patch("core.views.validate_data")
    mock.delay.return_value = Task()
    return mock


@pytest.fixture
def cleanup_upload_task(mocker):
    mock = mocker.patch("core.views.cleanup_upload")
    return mock


@pytest.fixture
def mocked_sleep(mocker):
    mock = mocker.patch("core.tasks.time.sleep")
    return mock


@pytest.fixture
def validation_obj():
    return Validation.objects.create()


@pytest.fixture
def upload_obj(validation_obj):
    return Upload.objects.create(filename="don.json", validation=validation_obj, expired_at=timezone.now())

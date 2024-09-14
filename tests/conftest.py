import json
import os
import pathlib
import shutil
import uuid

import pytest
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils import timezone
from spoonbill.stats import DataPreprocessor

from core.models import DataFile, Upload, Url, Validation
from core.utils import retrieve_tables

from .utils import Response, Task

DATA_DIR = pathlib.Path(__file__).parent / "data"

ANALYZED_DATA_PATH = DATA_DIR / "analyzed.dump"
SAMPLE_DATA_PATH = DATA_DIR / "sample-dataset.json"


@pytest.fixture
def schema():
    path = DATA_DIR.parents[1] / "data" / "schema.json"
    with open(path) as fd:
        return json.loads(fd.read())


@pytest.fixture
def dataset():
    with open(SAMPLE_DATA_PATH) as f:
        yield f


@pytest.fixture
def analyzed():
    with open(ANALYZED_DATA_PATH, "rb") as f:
        yield f


@pytest.fixture
def available_tables():
    spec = DataPreprocessor.restore(ANALYZED_DATA_PATH)
    _available_tables, unavailable_tables = retrieve_tables(spec)
    return _available_tables, unavailable_tables


@pytest.fixture
def validation_task(mocker):
    mock = mocker.patch("core.views.validate_data")
    mock.delay.return_value = Task()
    return mock


@pytest.fixture
def cleanup_upload_task(mocker):
    return mocker.patch("core.views.cleanup_upload")


@pytest.fixture
def download_datasource_task(mocker):
    return mocker.patch("core.views.download_data_source")


@pytest.fixture
def validation_obj():
    return Validation.objects.create()


@pytest.fixture
def upload_obj(validation_obj, dataset):
    file_ = File(dataset)
    file_.name = uuid.uuid4().hex
    file_obj = DataFile.objects.create(file=file_)
    obj = Upload.objects.create(validation=validation_obj, expired_at=timezone.now())
    obj.files.add(file_obj)
    obj.save()
    yield obj

    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, str(obj.id)), ignore_errors=True)


@pytest.fixture
def upload_obj_validated(upload_obj, analyzed, available_tables):
    file_ = ContentFile(analyzed.read())
    _available_tables, unavailable_tables = available_tables
    upload_obj.analyzed_file.save("new", file_)
    upload_obj.available_tables = _available_tables
    upload_obj.unavailable_tables = unavailable_tables
    upload_obj.save(update_fields=["available_tables", "unavailable_tables"])
    yield upload_obj

    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, str(upload_obj.id)), ignore_errors=True)


@pytest.fixture
def url_obj(validation_obj, dataset):
    return Url.objects.create(
        urls=["https://example.org/dataset.json"],
        analyzed_data_url="https://example.org/analyzed.json",
        validation=validation_obj,
        expired_at=timezone.now(),
    )


@pytest.fixture
def url_obj_w_files(url_obj, dataset, analyzed):
    file_ = File(dataset)
    file_.name = uuid.uuid4().hex
    analyzed_file_ = File(analyzed)
    analyzed_file_.name = uuid.uuid4().hex
    file_obj = DataFile.objects.create(file=file_)
    url_obj.files.add(file_obj)
    url_obj.analyzed_file = analyzed_file_
    url_obj.save()

    yield url_obj

    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, str(url_obj.id)), ignore_errors=True)


@pytest.fixture
def mocked_request(mocker, url_obj):
    request = mocker.patch("core.tasks.requests")
    path = os.path.dirname(__file__) + "/data/sample-dataset.json"
    with open(path) as f:
        data = f.read()
    response = Response(body=data)
    request.get.return_value = response
    yield request

    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, str(url_obj.id)), ignore_errors=True)

import os
import pathlib

import pytest
from django.conf import settings

from core.models import DataFile
from core.utils import gz_size, multiple_file_assigner

DATA_DIR = os.path.dirname(__file__) + "/data"
DATASET_PATH_GZ = f"{DATA_DIR}/sample-dataset.json.gz"
DATASET_PATH = f"{DATA_DIR}/sample-dataset.json"


@pytest.mark.django_db
def test_multiple_file_assigner():
    paths = ["data/file.json", "data/file1.json", "data/file2.json", "data/file3.json", "data/file4.json"]
    files = [DataFile.objects.create() for path in paths]

    files = multiple_file_assigner(files, paths)

    file_paths = [file.file.path for file in files]
    media_paths = [settings.MEDIA_ROOT + path for path in paths]

    assert file_paths == media_paths


def test_gz_size():
    gz_uncompressed_size = gz_size(DATASET_PATH_GZ)
    non_gz_file_size = pathlib.Path(DATASET_PATH).stat().st_size
    assert gz_uncompressed_size == non_gz_file_size

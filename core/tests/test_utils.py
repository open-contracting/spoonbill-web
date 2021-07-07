import pytest
from django.conf import settings

from core.models import DataFile
from core.utils import multiple_file_assigner


@pytest.mark.django_db
def test_multiple_file_assigner():
    paths = ["data/file.json", "data/file1.json", "data/file2.json", "data/file3.json", "data/file4.json"]
    files = [DataFile.objects.create() for path in paths]

    files = multiple_file_assigner(files, paths)

    file_paths = [file.file.path for file in files]
    media_paths = [settings.MEDIA_ROOT + path for path in paths]

    assert file_paths == media_paths

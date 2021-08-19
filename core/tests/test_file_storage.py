from unittest.mock import patch

import pytest
from django.core.exceptions import SuspiciousFileOperation

from core.file_storage import safe_join


@patch("core.file_storage.DATAREGISTRY_MEDIA_ROOT", "")
def test_safe_join_no_dataregistry_failed():
    media_root = "/tmp/media"
    path = "/tmp/dataregistry/file.json"
    with pytest.raises(SuspiciousFileOperation) as e:
        safe_join(media_root, path)
    assert f"The joined path ({path}) is located outside of the base path component ({media_root})" in str(e)


@patch("core.file_storage.DATAREGISTRY_MEDIA_ROOT", "")
def test_safe_join_no_dataregistry_success():
    media_root = "/tmp/media"
    path = "/tmp/media/dataregistry/file.json"
    assert safe_join(media_root, path) == path


@patch("core.file_storage.DATAREGISTRY_MEDIA_ROOT", "/tmp/dataregistry/")
def test_safe_join_with_dataregistry_failed():
    media_root = "/tmp/media"
    path = "/otherfolder/file.json"
    with pytest.raises(SuspiciousFileOperation) as e:
        safe_join(media_root, path)
    assert "The joined path is located outside of the allowed locations" in str(e)


@patch("core.file_storage.DATAREGISTRY_MEDIA_ROOT", "/tmp/dataregistry/")
def test_safe_join_with_dataregistry_success():
    media_root = "/tmp/media"
    path = "/tmp/dataregistry/file.json"
    assert safe_join(media_root, path) == path

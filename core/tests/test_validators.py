from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from core.validators import dataregistry_path_validator, validate_url_or_path


def test_validate_url_successful():
    url = "https://www.google.com"
    assert validate_url_or_path(url) is None


def test_validate_failed():
    url = "https://google"
    with pytest.raises(ValueError) as e:
        validate_url_or_path(url)
    assert "Input URL is invalid" in str(e)


def test_validate_unsupported_url():
    url = "ftps://www.link.com"
    with pytest.raises(NotImplementedError) as e:
        validate_url_or_path(url)
    assert "This type of URL is not supported yet" in str(e)


def test_dataregistry_path_validate_no_dataregistry_path():
    path = "file:///file.json"
    with pytest.raises(ValidationError) as e:
        dataregistry_path_validator(path)
    assert "No file found on this address" in str(e)


@patch("core.validators.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("core.utils.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
def test_dataregistry_path_validatator_non_existing_path():
    path = "file:///file.json"
    with pytest.raises(ValidationError) as e:
        dataregistry_path_validator(path)
    assert "No file found on this address" in str(e)


@patch("core.validators.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("core.utils.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("os.path.islink", return_value=True)
def test_dataregistry_path_validatator_symlink_not_allowed(mock_islink):
    path = "file:///file.json"
    with pytest.raises(ValidationError) as e:
        dataregistry_path_validator(path)
    assert "No file found on this address" in str(e)


@patch("core.validators.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("core.utils.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("core.validators.DATAREGISTRY_JAIL", False)
@patch("pathlib.Path.is_file", return_value=True)
def test_dataregistry_path_validatator_no_jail(mock_isfile):
    path = "file:///random/folder/file.json"
    result = dataregistry_path_validator(path)
    assert result is None


@patch("core.validators.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("core.utils.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("pathlib.Path.is_file", return_value=True)
def test_dataregistry_path_validatator_success(mock_isfile):
    path = "file:///tmp/data_registry/file.json"
    result = dataregistry_path_validator(path)
    assert result is None


@patch("core.validators.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
@patch("core.utils.DATAREGISTRY_MEDIA_ROOT", "/tmp/data_registry/")
def test_dataregistry_path_validatator_attribute_error():
    path = ["file1.rar", "file2.txt"]
    with pytest.raises(ValidationError) as e:
        dataregistry_path_validator(path)
    assert "No file found on this address" in str(e)

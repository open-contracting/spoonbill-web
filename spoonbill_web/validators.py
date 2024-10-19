import os
import pathlib
from os.path import commonprefix

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from spoonbill_web.utils import dataregistry_path_formatter, dataregistry_path_resolver, get_protocol


def dataregistry_path_validator(path):
    _message = "No file found on this address"
    if settings.DATAREGISTRY_MEDIA_ROOT is None:
        raise ValidationError(_message)
    try:
        # Formatting full path
        path = dataregistry_path_formatter(path)
        # Symlink validation
        if not settings.DATAREGISTRY_ALLOW_SYMLINKS and os.path.islink(path):
            raise ValidationError(_message)
        # Resolving path
        path = dataregistry_path_resolver(path)

        # Skip check if jail is off
        if not settings.DATAREGISTRY_JAIL and pathlib.Path(path).is_file():
            return
        # Path validation
        reg_dir = str(settings.DATAREGISTRY_MEDIA_ROOT)
        if settings.DATAREGISTRY_ALLOW_SYMLINKS and os.path.islink(reg_dir):
            reg_dir = str(dataregistry_path_resolver(reg_dir))

        reg_dir = reg_dir.rstrip(reg_dir[-1]) if reg_dir[-1] == "/" else reg_dir

        if (
            commonprefix([path, pathlib.Path(reg_dir)]) == str(pathlib.Path(reg_dir))
            and str(os.path.dirname(path)).startswith(reg_dir)
            and pathlib.Path(path).is_file()
        ):
            return
        raise ValidationError(_message)
    except (TypeError, AttributeError) as e:
        raise ValidationError(_message) from e


def validate_url_or_path(url):
    validators = {"http": URLValidator(), "https": URLValidator(), "file": dataregistry_path_validator}
    protocol = get_protocol(url)

    validator = validators.get(protocol)
    if not validator:
        raise NotImplementedError("This type of URL is not supported yet")
    try:
        validator(url)
    except (ValidationError, AttributeError) as e:
        raise ValueError("Input URL is invalid") from e


def url_multi_upload_validator(array):
    if len(array) > 1:
        for path in array:
            if get_protocol(path) != "file":
                raise ValidationError("Multiple uploads are not available for this type of URL")

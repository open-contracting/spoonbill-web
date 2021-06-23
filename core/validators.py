import os
import pathlib
from os.path import commonprefix
from urllib.parse import unquote, urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from core.utils import dataregistry_path_formatter, dataregistry_path_resolver, get_protocol

DATAREGISTRY_ALLOW_SYMLINKS = settings.DATAREGISTRY_ALLOW_SYMLINKS
DATAREGISTRY_MEDIA_ROOT = settings.DATAREGISTRY_MEDIA_ROOT
DATAREGISTRY_JAIL = settings.DATAREGISTRY_JAIL


def dataregistry_path_validator(path):

    _message = "No file found on this address"
    if DATAREGISTRY_MEDIA_ROOT is None:
        raise ValidationError(_message)
    try:
        # Formatting full path
        path = dataregistry_path_formatter(path)
        # Symlink validation
        if os.path.islink(path) and DATAREGISTRY_ALLOW_SYMLINKS is False:
            raise ValidationError(_message)
        # Resolving path
        path = dataregistry_path_resolver(path)

        # Skip check if jail is off
        if DATAREGISTRY_JAIL is False and pathlib.Path(path).is_file():
            return
        # Path validation
        reg_dir = str(DATAREGISTRY_MEDIA_ROOT)
        reg_dir = reg_dir.rstrip(reg_dir[-1]) if reg_dir[-1] == "/" else reg_dir

        if (
            commonprefix([path, DATAREGISTRY_MEDIA_ROOT]) == str(DATAREGISTRY_MEDIA_ROOT)
            and str(os.path.dirname(path)) == reg_dir
            and pathlib.Path(path).is_file()
        ):
            return
        raise ValidationError(_message)
    except (TypeError, AttributeError):
        raise ValidationError(_message)


def validate_url_or_path(url):
    validators = {"http": URLValidator(), "https": URLValidator(), "file": dataregistry_path_validator}
    protocol = get_protocol(url)

    validator = validators.get(protocol)
    if not validator:
        raise NotImplementedError("This type of URL is not supported yet")
    try:
        validator(url)
        return
    except (ValidationError, AttributeError):
        raise ValueError("Input URL is invalid")

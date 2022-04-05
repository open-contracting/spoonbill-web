import os
from os.path import abspath, dirname, join, normcase, sep

from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import FileSystemStorage

from core.utils import dataregistry_path_resolver
from spoonbill_web.settings.settings import DATAREGISTRY_ALLOW_SYMLINKS, DATAREGISTRY_MEDIA_ROOT


def safe_join(base, *paths):
    """
    Based on django/utils/_os/safe_join
    Modified to include dataregistry functionality
    """
    final_path = abspath(join(base, *paths))
    base_path = abspath(base)

    # Validate with MEDIA_ROOT
    if (
        not normcase(final_path).startswith(normcase(base_path + sep))
        and normcase(final_path) != normcase(base_path)
        and dirname(normcase(base_path)) != normcase(base_path)
    ):

        if DATAREGISTRY_MEDIA_ROOT:
            # Validate with DATAREGISTRY_MEDIA_ROOT
            data_registry_path = abspath(DATAREGISTRY_MEDIA_ROOT)
            if DATAREGISTRY_ALLOW_SYMLINKS is True and os.path.islink(data_registry_path):
                data_registry_path = abspath(dataregistry_path_resolver(data_registry_path))
            if (
                not normcase(final_path).startswith(normcase(data_registry_path + sep))
                and normcase(final_path) != normcase(data_registry_path)
                and dirname(normcase(data_registry_path)) != normcase(data_registry_path)
            ):
                raise SuspiciousFileOperation("The joined path is located outside of the allowed locations")
            else:
                return final_path

        raise SuspiciousFileOperation(
            f"The joined path ({final_path}) is located outside of the base path component ({base_path})"
        )
    return final_path


class MediaAndDataregistryFS(FileSystemStorage):
    """
    Custom file storage, 'path' method is using modified 'safe_join' with included dataregistry functionality
    """

    def path(self, name):
        return safe_join(self.location, name)

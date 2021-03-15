import os

from django.conf import settings


def handle_upload_file(f, dirname):
    os.mkdir(f"{settings.UPLOAD_PATH_PREFIX}{dirname}")
    path = f"{settings.UPLOAD_PATH_PREFIX}{dirname}/{f.name}"

    with open(path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

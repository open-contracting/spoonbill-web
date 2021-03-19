import uuid


def instance_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    return "{0}/{1}.json".format(instance.id, uuid.uuid4().hex)

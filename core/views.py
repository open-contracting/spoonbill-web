from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.models import Upload, Validation
from core.serializers import UploadSerializer
from core.tasks import cleanup_upload, validate_data
from core.utils import handle_upload_file


class UploadViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permissions_classes = permissions.AllowAny
    lookup_field = "id"
    http_method_names = ["get", "post", "head", "options", "trace"]
    serializer_class = UploadSerializer
    queryset = Upload.objects.all()
    parser_classes = [MultiPartParser]

    def retrieve(self, request, id=None, *args, **kwargs):
        serializer = self.get_serializer_class()(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            if not request.FILES.get("file"):
                return Response({"detail": _("File is required")}, status=status.HTTP_400_BAD_REQUEST)
            data = {"filename": request.FILES["file"].name}
            serializer = self.get_serializer_class()(data=data)
            if serializer.is_valid():
                validation_obj = Validation.objects.create()
                upload_obj = Upload.objects.create(**serializer.data)
                handle_upload_file(request.FILES["file"], upload_obj.id)

                task = validate_data.delay(upload_obj.id, validation_obj.id)
                validation_obj.task_id = task.id
                validation_obj.save(update_fields=["task_id"])

                upload_obj.validation = validation_obj
                upload_obj.expired_at = timezone.now() + timedelta(days=settings.UPLOAD_TIMEDELTA)
                upload_obj.save(update_fields=["validation", "expired_at"])

                cleanup_upload.apply_async((upload_obj.id,), eta=upload_obj.expired_at)
                return Response(
                    self.get_serializer_class()(upload_obj).data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

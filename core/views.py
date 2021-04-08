import csv
import json
import os
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.models import DataSelection, Table, Upload, Url, Validation
from core.serializers import DataSelectionSerializer, TablesSerializer, UploadSerializer, UrlSerializer
from core.tasks import cleanup_upload, download_data_source, validate_data


class UploadViewSet(viewsets.GenericViewSet):
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
            file_ = File(request.FILES["file"])
            validation_obj = Validation.objects.create()
            upload_obj = Upload.objects.create(file=file_, validation=validation_obj)
            task = validate_data.delay(upload_obj.id, model="Upload")
            validation_obj.task_id = task.id
            validation_obj.save(update_fields=["task_id"])

            upload_obj.validation = validation_obj
            upload_obj.expired_at = timezone.now() + timedelta(days=settings.UPLOAD_TIMEDELTA)
            upload_obj.save(update_fields=["validation", "expired_at"])
            cleanup_upload.apply_async((upload_obj.id, "Upload"), eta=upload_obj.expired_at)
            return Response(
                self.get_serializer_class()(upload_obj).data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)


class URLViewSet(viewsets.GenericViewSet):
    """URL based datasource

    This endpoint allows providing URLs for the dataset file and analyzed dataset file which is placed in some cloud
    services or data registries (data lakes) that provide HTTP access for their data.

    For providing a dataset placed somewhere on the Internet it is enough to provide a URL attribute in the body of
    the POST request.

    **Example (data from some cloud):**
    ```python
    >>> import requests
    >>> response = request.post('/urls/', {'url': 'https://<filehosting.host>/<json-file>'})
    >>> response.json()
    {
        "id": "96224033-73ef-430a-bc46-67cd205f249f",
        "validation": {
            "id": "642149d1-2488-493c-927c-f29f875ac3a6",
            "task_id": None,
            "is_valid": None,
            "errors": None
        },
        "url": "https://<filehosting.host>/<json-file>",
        "analyzed_data_url": "",
        "analyzed_data_file": None,
        "data_file": None,
        "status": "queued.download",
        "created_at": "2021-03-19T10:42:48.265943Z",
        "expired_at": None,
        "deleted": False,
        "downloaded": False,
        "error": None
    }

    ```

    **Example (data from OCDS data registry):**
    ```python
    >>> response = request.post('/urls/', {'url': 'https://<data-registry.host>/<dataset-query>',
                                           'analyzed_data_url': 'https://<data-registry.host>/<analyzed-data-query>'})
    >>> response.json()
    {
        "id": "cb82da20-1aa2-4574-a8f7-3fbe92c7b412",
        "validation": {
            "id": "f961e1c2-69f0-408e-989a-cd7d50c497c2",
            "task_id": None,
            "is_valid": None,
            "errors": None
        },
        "url": "https://<data-registry.host>/<dataset-query>",
        "analyzed_data_url": "https://<data-registry.host>/<analyzed-data-query>",
        "analyzed_data_file": None,
        "data_file": None,
        "status": "queued.download",
        "created_at": "2021-03-19T10:51:39.482275Z",
        "expired_at": None,
        "deleted": False,
        "downloaded": False,
        "error": None
    }

    ```
    """

    permissions_classes = permissions.AllowAny
    lookup_field = "id"
    http_method_names = ["get", "post", "head", "options", "trace"]
    serializer_class = UrlSerializer
    queryset = Url.objects.all()

    def retrieve(self, request, id=None, *args, **kwargs):
        serializer = self.get_serializer_class()(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            url = request.POST.get("url", "") or request.data.get("url", "")
            if not url:
                return Response({"detail": _("Url is required")}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer_class()(data=request.POST or request.data)
            if serializer.is_valid():
                validation_obj = Validation.objects.create()
                url_obj = Url.objects.create(**serializer.data)
                url_obj.validation = validation_obj
                url_obj.save(update_fields=["validation"])
                download_data_source.delay(url_obj.id, model="Url")
                return Response(self.get_serializer_class()(url_obj).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)


class DataSelectionViewSet(viewsets.ModelViewSet):
    serializer_class = DataSelectionSerializer
    queryset = DataSelection.objects.all()
    lookup_field = "id"
    http_method_names = ["get", "post", "head", "options", "trace"]

    def create(self, request, *args, upload_id=None, url_id=None):
        serializer = self.get_serializer_class()(data=request.data or request.POST)
        if serializer.is_valid():
            ds = DataSelection.objects.create()
            for table in request.data.get("tables", []):
                tb = Table.objects.create(**table)
                ds.tables.add(tb)
            if upload_id:
                ds.upload_set.add(upload_id)
            elif url_id:
                ds.url_set.add(url_id)
            return Response(self.get_serializer_class()(ds).data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, url_id=None, upload_id=None):
        if url_id:
            queryset = DataSelection.objects.filter(url=url_id)
            serializer = DataSelectionSerializer(queryset, many=True)
        elif upload_id:
            queryset = DataSelection.objects.filter(upload=upload_id)
            serializer = DataSelectionSerializer(queryset, many=True)
        return Response(serializer.data)


class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TablesSerializer
    queryset = Table.objects.all()
    http_method_names = ["get", "patch", "head", "options", "trace"]
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        queryset = Table.objects.filter(dataselection=kwargs.get("selection_id", ""))
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if "url_id" in kwargs:
            datasource = Url.objects.get(id=kwargs["url_id"])
        elif "upload_id" in kwargs:
            datasource = Upload.objects.get(id=kwargs["upload_id"])
        table = Table.objects.get(id=kwargs["id"])
        with open(datasource.analyzed_file.path) as fd:
            data = json.loads(fd.read())
        datasource_dir = os.path.dirname(datasource.file.path)
        tables = data["tables"]
        root_table = tables.get(table.name, {})
        for table_key in root_table.get("child_tables", []):
            headers = [h for h in tables[table_key]["combined_columns"] if "1" not in h]
            preview_path = f"{datasource_dir}/{table_key}.csv"
            with open(preview_path, "w", newline="\n") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(tables[table.name]["preview_rows_combined"])


class TablePreviewViewSet(viewsets.GenericViewSet):
    queryset = Table.objects.all()
    http_method_names = ["get", "head", "options", "trace"]

    def list(self, request, url_id=None, upload_id=None, selection_id=None, table_id=None):
        table = Table.objects.get(id=table_id)
        if url_id:
            datasource = Url.objects.get(id=url_id)
        elif upload_id:
            datasource = Upload.objects.get(id=upload_id)
        datasource_dir = os.path.dirname(datasource.file.path)
        with open(datasource.analyzed_file.path) as fd:
            analyzed_data = json.loads(fd.read())
        tables = analyzed_data["tables"]
        data = []
        # table_name_lower = table.name.lower()
        try:
            if table.split:
                for letter in ("a", "b", "c"):
                    data.append(
                        {
                            "name": f"{table.name.title()}_{letter}.csv",
                            "id": str(table.id),
                            "preview": "col1,col2,col3\ncell11,cell12,cell13\ncell21,cell22,cell23",
                        }
                    )
            #     for filename in os.listdir(datasource_dir):
            #         if filename.startswith(table_name_lower):
            #             with open(f"{datasource_dir}/{filename}") as f:
            #                 data.append({"name": filename.title(), "preview": f.read()})
            else:
                headers = [h for h in tables[table.name]["combined_columns"] if "1" not in h]
                preview_path = f"{datasource_dir}/{table.name}.csv"
                with open(preview_path, "w", newline="\n") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(tables[table.name]["preview_rows_combined"])
                with open(preview_path) as csvfile:
                    data.append(
                        {
                            "name": f"{tables[table.name]['name']}.csv",
                            "id": str(table.id),
                            "preview": csvfile.read(),
                        }
                    )
        except FileNotFoundError:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)

import json
import logging
import os
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.models import DataSelection, Flatten, Table, Upload, Url, Validation
from core.serializers import (
    DataSelectionSerializer,
    FlattenSerializer,
    TablesSerializer,
    UploadSerializer,
    UrlSerializer,
)
from core.tasks import cleanup_upload, download_data_source, flatten_data, validate_data
from core.utils import set_column_headings, store_preview_csv

COLUMNS = "columns"
COMBINED_COLUMNS = "combined_columns"
COMBINED_PREVIEW_ROWS = "preview_rows_combined"
PREVIEW_ROWS = "preview_rows"

logger = logging.getLogger(__name__)


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
            lang_code = get_language()
            task = validate_data.delay(upload_obj.id, model="Upload", lang_code=lang_code)
            validation_obj.task_id = task.id
            validation_obj.save(update_fields=["task_id"])

            upload_obj.validation = validation_obj
            upload_obj.expired_at = timezone.now() + timedelta(days=settings.JOB_FILES_TIMEOUT)
            upload_obj.save(update_fields=["validation", "expired_at"])
            cleanup_upload.apply_async((upload_obj.id, "Upload", lang_code), eta=upload_obj.expired_at)
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
                lang_code = get_language()
                download_data_source.delay(url_obj.id, model="Url", lang_code=lang_code)
                return Response(self.get_serializer_class()(url_obj).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)


class DataSelectionViewSet(viewsets.ModelViewSet):
    serializer_class = DataSelectionSerializer
    queryset = DataSelection.objects.all()
    lookup_field = "id"
    http_method_names = ["get", "post", "patch", "head", "options", "trace"]

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

    def update(self, request, *args, **kwargs):
        ds = DataSelection.objects.get(id=kwargs.get("id"))
        if "headings_type" in request.data and ds.headings_type != request.data["headings_type"]:
            types = [t[0] for t in ds.HEADING_TYPES]
            headings_type = request.data["headings_type"]
            if headings_type not in types:
                return Response(
                    {"detail": _("Please use for column_heading value one of %s") % types},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ds.headings_type = request.data["headings_type"]
            ds.save(update_fields=["headings_type"])
            if "url_id" in kwargs:
                source = Url.objects.get(id=kwargs["url_id"])
            elif "upload_id" in kwargs:
                source = Upload.objects.get(id=kwargs["upload_id"])
            set_column_headings(ds, source.analyzed_file.path)
        serializer = DataSelectionSerializer(ds)
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
        tables = data["tables"]
        update_fields = []
        for key in ("split", "include", "heading"):
            if key in request.data:
                setattr(table, key, request.data[key])
                update_fields.append(key)
        if update_fields:
            table.save(update_fields=update_fields)
        is_array_tables = len(table.array_tables.all())
        if "split" in request.data and request.data["split"] and not is_array_tables:
            child_tables = tables.get(table.name, {}).get("child_tables", [])
            self._split_table(table, tables, datasource, child_tables)
        serializer = self.get_serializer_class()(table)
        return Response(serializer.data)

    def _split_table(self, table, analyzed_tables, datasource, child_tables):
        datasource_dir = os.path.dirname(datasource.file.path)
        for child_table_key in child_tables:
            analyzed_child_table = analyzed_tables.get(child_table_key, {})
            if analyzed_child_table.get("total_rows", 0) == 0:
                logger.debug(
                    "Skip child table %s for datasource %s" % (child_table_key, datasource),
                    extra={
                        "MESSAGE_ID": "skip_child_table",
                        "TABLE_KEY": child_table_key,
                        "DATASOURCE_ID": str(datasource.id),
                        "MODEL": datasource.__class__.__name__,
                    },
                )
                continue
            child_table = Table.objects.create(name=child_table_key)
            table.array_tables.add(child_table)
            preview_path = f"{datasource_dir}/{child_table_key}_combined.csv"
            store_preview_csv(COMBINED_COLUMNS, PREVIEW_ROWS, analyzed_tables[child_table_key], preview_path)
            if analyzed_child_table.get("child_tables", []):
                self._split_table(table, analyzed_tables, datasource, analyzed_child_table["child_tables"])


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
        selection = DataSelection.objects.get(id=selection_id)
        with open(datasource.analyzed_file.path) as fd:
            analyzed_data = json.loads(fd.read())
        tables = analyzed_data["tables"]
        data = []
        if table.split:
            preview_path = f"{datasource_dir}/{table.name}.csv"
            if not os.path.exists(preview_path):
                store_preview_csv(COLUMNS, PREVIEW_ROWS, tables[table.name], preview_path)
            with open(preview_path) as csvfile:
                preview = {
                    "name": tables[table.name]["name"],
                    "id": str(table.id),
                    "preview": csvfile.read(),
                    "heading": table.heading,
                }
                if selection.headings_type != selection.OCDS:
                    preview["column_headings"] = table.column_headings
            data.append(preview)
            for child_table in table.array_tables.all():
                if not child_table.include:
                    continue
                preview_path = f"{datasource_dir}/{child_table.name}_combined.csv"
                with open(preview_path) as csvfile:
                    preview = {
                        "name": tables[child_table.name]["name"],
                        "id": str(child_table.id),
                        "preview": csvfile.read(),
                        "heading": child_table.heading,
                    }
                    if selection.headings_type != selection.OCDS:
                        preview["column_headings"] = child_table.column_headings
                data.append(preview)
        else:
            preview_path = f"{datasource_dir}/{table.name}_combined.csv"
            if not os.path.exists(preview_path):
                store_preview_csv(COMBINED_COLUMNS, COMBINED_PREVIEW_ROWS, tables[table.name], preview_path)
            with open(preview_path) as csvfile:
                preview = {
                    "name": tables[table.name]["name"],
                    "id": str(table.id),
                    "preview": csvfile.read(),
                    "heading": table.heading,
                }
                if selection.headings_type != selection.OCDS:
                    preview["column_headings"] = table.column_headings
                data.append(preview)
        return Response(data)


class FlattenViewSet(viewsets.GenericViewSet):
    serializer_class = FlattenSerializer
    queryset = Flatten.objects.all()
    http_method_names = ["get", "patch", "post", "head", "options", "trace"]
    lookup_field = "id"

    def retrieve(self, request, id=None, *args, **kwargs):
        serializer = self.get_serializer_class()(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data or request.POST)
        if serializer.is_valid():
            selection = DataSelection.objects.get(id=kwargs["selection_id"])
            selection.flatten_types
            flatten_type = serializer.data.get("export_format", Flatten.XLSX)
            if flatten_type in selection.flatten_types:
                return Response(
                    {"detail": _("Flatten request for this type already exists.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            flatten = Flatten.objects.create(**serializer.data)
            selection.flattens.add(flatten)
            serializer = self.get_serializer_class()(flatten)
            model = "Upload" if "upload_id" in kwargs else "Url"
            lang_code = get_language()
            flatten_data.delay(flatten.id, model=model, lang_code=lang_code)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            flatten = Flatten.objects.get(id=kwargs["id"])
            new_status = request.data.get("status", "")
            if flatten.status not in (Flatten.FAILED, Flatten.COMPLETED):
                return Response(
                    {"detail": _("You can't reschedule flatten in (%s) status") % flatten.status},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif new_status != Flatten.SCHEDULED:
                return Response(
                    {"detail": _("You can set status to %s only") % Flatten.SCHEDULED},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            flatten.status = Flatten.SCHEDULED
            flatten.save(update_fields=["status"])
            model = "Upload" if "upload_id" in kwargs else "Url"
            lang_code = get_language()
            flatten_data.delay(flatten.id, model=model, lang_code=lang_code)
            self.get_serializer_class()(flatten)
            return Response(serializer.data)
        else:
            return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = Flatten.objects.filter(dataselection=kwargs.get("selection_id", ""))
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

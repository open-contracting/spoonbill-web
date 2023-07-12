import errno
import logging
import os
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from spoonbill.common import TABLE_THRESHOLD
from spoonbill.stats import DataPreprocessor

from core.constants import OCDS_LITE_CONFIG
from core.models import DataFile, DataSelection, Flatten, Table, Upload, Url, Validation
from core.serializers import (
    DataSelectionSerializer,
    FlattenSerializer,
    TablesSerializer,
    UploadSerializer,
    UrlSerializer,
)
from core.tasks import cleanup_upload, download_data_source, flatten_data, validate_data
from core.utils import get_protocol, set_column_headings, store_preview_csv

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
            if "files" not in request.FILES:
                return Response({"detail": _("File is required")}, status=status.HTTP_400_BAD_REQUEST)
            if len(request.FILES.getlist("files")) > 1:
                return Response(
                    {"detail": _("Multi-upload feature is not available for file uploads yet. Stay tuned!")},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
            lang_code = get_language()
            validation_obj = Validation.objects.create()
            expired_at = timezone.now() + timedelta(days=settings.JOB_FILES_TIMEOUT)
            upload_obj = Upload.objects.create(expired_at=expired_at, validation=validation_obj)
            cleanup_upload.apply_async((upload_obj.id, "Upload", lang_code), eta=upload_obj.expired_at)

            if isinstance(request.FILES["files"], TemporaryUploadedFile):
                _empty_file = ContentFile(b"")
                file_obj = DataFile.objects.create()
                file_obj.file.save("new", _empty_file)
                upload_obj.files.add(file_obj)
                _file = request.FILES["files"]
                initial_path = _file.file.name
                os.rename(initial_path, upload_obj.files.all()[0].file.path)
                _file.close()
            else:
                file_ = File(request.FILES["files"])
                file_obj = DataFile.objects.create()
                file_obj.file.save("new", file_)
                upload_obj.files.add(file_obj)
                upload_obj.save()

            task = validate_data.delay(upload_obj.id, model="Upload", lang_code=lang_code)
            validation_obj.task_id = task.id
            validation_obj.save(update_fields=["task_id"])

            upload_obj.validation = validation_obj
            upload_obj.save(update_fields=["validation"])
            return Response(
                self.get_serializer_class()(upload_obj).data,
                status=status.HTTP_201_CREATED,
            )
        except (OSError, Exception) as error:
            extra = {"MESSAGE_ID": "receiving_file_failed", "ERROR_MSG": str(error)}
            if hasattr(error, "errno") and error.errno == errno.ENOSPC:
                logger.info("Error while receiving file %s" % str(error), extra=extra)
                return Response(
                    {"detail": _("Currently, the space limit was reached. Please try again later.")},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
            else:
                logger.exception("Error while receiving file %s" % str(error), extra=extra)
                return Response(
                    {"detail": _("Error while receiving file. Contact our support service")},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


class URLViewSet(viewsets.GenericViewSet):
    """
    ##URL based datasource

    This endpoint allows providing URLs for the dataset file and analyzed dataset file which is placed in some cloud
    services or data registries (data lakes) that provide HTTP access for their data.

    For providing a dataset placed somewhere on the Internet it is enough to provide a URL attribute in the body of
    the POST request.

    Also, you may add optional info to respective fields, such as 'country', 'period' and 'source'

    **Example (data from some cloud):**
    ```python
    >>> import requests
    >>> response = request.post('/urls/',
                                {'urls': [ 'https://<filehosting.host>/<json-file>' ]},
                                headers={'Accept-Language': 'en_US|es'})
    >>> response.json()
    {
        "id": "96224033-73ef-430a-bc46-67cd205f249f",
        "validation": {
            "id": "642149d1-2488-493c-927c-f29f875ac3a6",
            "task_id": None,
            "is_valid": None,
            "errors": None
        },
        "urls": [ "https://<filehosting.host>/<json-file>" ],
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
    >>> response = request.post('/urls/',
                                {'urls': ['https://<data-registry.host>/<dataset-query>'],
                                 'analyzed_data_url': 'https://<data-registry.host>/<analyzed-data-query>',
                                 'country': 'United Kingdom',
                                 'period': 'Last 6 months',
                                 'source': 'OCP Kingfisher Database'
                                 },
                                headers={'Accept-Language': 'en_US|es'})
    >>> response.json()
    {
        "id": "cb82da20-1aa2-4574-a8f7-3fbe92c7b412",
        "validation": {
            "id": "f961e1c2-69f0-408e-989a-cd7d50c497c2",
            "task_id": None,
            "is_valid": None,
            "errors": None
        },
        "urls": [ "https://<data-registry.host>/<dataset-query>" ],
        "analyzed_data_url": "https://<data-registry.host>/<analyzed-data-query>",
        "analyzed_data_file": None,
        "data_file": None,
        "status": "queued.download",
        "created_at": "2021-03-19T10:51:39.482275Z",
        "expired_at": None,
        "deleted": False,
        "downloaded": False,
        "error": None,
        "available_tables": None,
        "unavailable_tables": [],
        "root_key": None,
        "country": "United Kingdom",
        "period": "Last 6 months",
        "source": "OCP Kingfisher Database"
    }
    ```

    After receiving this response you need to redirect user to the following URL:
    `https://<spoonbill-web.host>/#/upload-file?lang=<lang-code>&url=<received-id>`
    e.g. `https://<spoonbill-web.host>/#/upload-file?lang=en_US|es&url=cb82da20-1aa2-4574-a8f7-3fbe92c7b412`

    ## Dataregistry path URLs

    You may pass the URL field path to a file, that is located in dataregistry folder.
    Links for these files should look like this:
    `file:///absolute/path/to/a/file/within/dataregistry/folder/document.json` \n
    (absolute path, note 3 slashes after `file:`), or \n
    `file://document.json` \n
     (relative path, if file is located within the dataregistry folder).

    **Example of json request body:**

    ```python
    {"urls":
        [
            "file://file.json"
        ]
    }
    ```

    Multiple path URLs may be passed at once as well:
    ```python
    {"urls":
        [
            "file://file.json",
            "file:///mnt/big-hdd/dataregistry/prozorro/2020.json",
            "file://file2.json",
            "file://file3.json",
            "file://file4.json"
        ]
    }
    ```
    ## **Authorization**
    Only authorized users are allowed to use file URIs (ones that starts with `file://`).
    User's request may be authorized through HTTP Basic Authorization.
    In order to send authorized request - HTTP header should include 'Authorization' field;
    and base64-encoded credentials: \n
    `"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="` \n
    Please note, that user's credentials are regular username and password,
    but those should be encoded before sending a request.
    Example of encoding credentials you may see below
    ### **Example of authorized request with encoded credentials (python script)**
    ```python
    import requests

    username = 'johhsmith'
    password = 'youshallnotpass'

    response = requests.post('/urls/',
                             {'urls': ["file://document.json"]},
                             auth=(username, password))
    print(response.json())
    ```
    Through terminal commands you may create, delete or edit users in database.

    ### **Creating new users**
    ```cli
    $ python manage.py shell
    >>>from django.contrib.auth.models import User
    >>>user = User.objects.create_user(username='john', password='johnpassword')
    >>>user.save()
    >>>exit()
    ```

    ### **Delete user**
    ```cli
    $ python manage.py shell
    >>>from django.contrib.auth.models import User
    >>>user = User.objects.get(username='john')
    >>>user.delete()
    >>>exit()
    ```

    ### **Change user's password**
    ```cli
    $ python manage.py changepassword john
    Changing password for user 'john'
    Password: <password>
    Password (again): <password>
    Password changed successfully for user 'john'
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
            urls = request.POST.get("urls", "") or request.data.get("urls", "")
            if not urls:
                return Response({"detail": _("Url is required")}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer_class()(data=request.POST or request.data)
            if serializer.is_valid():
                validation_obj = Validation.objects.create()
                url_obj = Url.objects.create(**serializer.validated_data)
                protocol = get_protocol(serializer.validated_data["urls"][0])
                if request.user.is_authenticated:
                    url_obj.author = request.user
                elif protocol == "file":
                    return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
                else:
                    url_obj.author = None
                url_obj.validation = validation_obj
                url_obj.save(update_fields=["validation", "author"])
                lang_code = get_language()
                download_data_source.delay(url_obj.id, model="Url", lang_code=lang_code)
                return Response(self.get_serializer_class()(url_obj).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)


class DataSelectionViewSet(viewsets.GenericViewSet):
    serializer_class = DataSelectionSerializer
    queryset = DataSelection.objects.all()
    lookup_field = "id"
    http_method_names = ["get", "post", "patch", "head", "options", "trace"]

    def retrieve(self, request, id=None, *args, **kwargs):
        serializer = self.get_serializer_class()(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, upload_id=None, url_id=None):
        data = request.data or request.POST
        kind = data.get("kind", DataSelection.CUSTOM)
        headings_type = DataSelection.OCDS

        if kind != DataSelection.OCDS_LITE:
            serializer = self.get_serializer_class()(data=data)
            if serializer.is_valid():
                datasource = Url.objects.get(id=url_id) if url_id else Upload.objects.get(id=upload_id)
                selection = DataSelection.objects.create(kind=kind, headings_type=headings_type)
                spec = DataPreprocessor.restore(datasource.analyzed_file.path)
                for table in serializer.data["tables"]:
                    _table = Table.objects.create(**table)
                    _table.should_split = spec[_table.name].splitted
                    _table.save()
                    selection.tables.add(_table)
                datasource.selections.add(selection)
                return Response(self.get_serializer_class()(selection).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            datasource = Url.objects.get(id=url_id) if url_id else Upload.objects.get(id=upload_id)
            if not datasource.available_tables:
                return Response(
                    {"detail": _("Datasource without available tables")}, status=status.HTTP_400_BAD_REQUEST
                )
            lang_code = get_language()
            lang_prefix = lang_code.split("-")[0]
            headings_type = f"{lang_prefix}_user_friendly"
            selection = DataSelection.objects.create(kind=kind, headings_type=headings_type)
            spec = DataPreprocessor.restore(datasource.analyzed_file.path)
            for available_table in datasource.available_tables:
                if available_table["name"] in OCDS_LITE_CONFIG["tables"]:
                    _name = available_table["name"]
                    _split = OCDS_LITE_CONFIG["tables"][_name].get("split", False)
                    _table = Table.objects.create(name=_name, split=_split)
                    child_tables_data = spec.tables[_name].child_tables
                    if _split and child_tables_data:
                        for child_table in child_tables_data:
                            _include = (
                                False
                                if child_table not in OCDS_LITE_CONFIG["tables"][_name].get("child_tables", {})
                                else True
                            )
                            _child_table = Table.objects.create(name=child_table, include=_include)
                            _table.array_tables.add(_child_table)
                    selection.tables.add(_table)
            datasource.selections.add(selection)
            return Response(self.get_serializer_class()(selection).data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, url_id=None, upload_id=None):
        if url_id:
            queryset = DataSelection.objects.filter(url=url_id)
            serializer = DataSelectionSerializer(queryset, many=True)
        elif upload_id:
            queryset = DataSelection.objects.filter(upload=upload_id)
            serializer = DataSelectionSerializer(queryset, many=True)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
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
            ds.flattens.all().delete()
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
        try:
            datasource = (
                Url.objects.get(id=kwargs["url_id"])
                if "url_id" in kwargs
                else Upload.objects.get(id=kwargs["upload_id"])
            )
            table = Table.objects.get(id=kwargs["id"])
            spec = DataPreprocessor.restore(datasource.analyzed_file.path)
            update_fields = []
            for key in ("split", "include", "heading"):
                if key in request.data:
                    setattr(table, key, request.data[key])
                    # Remove "grandchildren" (child tables of child tables) if such are present
                    if key in ("split", "include") and request.data[key] is False:
                        if table.array_tables and not table.parent:
                            for array_table in list(table.array_tables.all()):
                                setattr(array_table, key, False)
                                array_table.save()
                        if table.array_tables and table.parent:
                            parent = table.array_tables.all()[0]
                            for array_table in list(parent.array_tables.all()):
                                setattr(
                                    array_table,
                                    key,
                                    False if array_table.parent == table.name else getattr(array_table, key),
                                )
                                array_table.save()
                    # Forbid merge of table if any of child arrays is unmergeable
                    if (
                        key == "split"
                        and request.data[key] is False
                        and table.array_tables
                        and False
                        in [_table.mergeable for _table in list(table.array_tables.all()) if _table.include is True]
                    ):
                        return Response(
                            {
                                "detail": _("Cannot merge '%(table_name)s' - child arrays are too large")
                                % {"table_name": table.name}
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    update_fields.append(key)
            if update_fields:
                table.save(update_fields=update_fields)
            is_array_tables = len(table.array_tables.all())
            if "split" in request.data and request.data["split"] and not is_array_tables:
                child_tables = spec.tables[table.name].child_tables
                self._split_table(table, spec.tables, datasource, child_tables)
            serializer = self.get_serializer_class()(table)
            sources = table.dataselection_set.all() or table.array_tables.all()[0].dataselection_set.all()
            if sources:
                sources[0].flattens.all().delete()
            return Response(serializer.data)
        except FileNotFoundError as e:
            extra = {
                "MESSAGE_ID": "update_table_failed",
                "DATASOURCE_ID": str(datasource.id),
                "TABLE_ID": kwargs["id"],
                "ERROR_MSG": str(e),
                "EXPIRED_AT": datasource.expired_at.isoformat(),
            }
            logger.info("Error while update table %s" % str(e), extra=extra)
            return Response({"detail": _("Datasource expired.")}, status=status.HTTP_404_NOT_FOUND)
        except OSError as e:
            extra = {
                "MESSAGE_ID": "update_table_failed",
                "DATASOURCE_ID": str(datasource.id),
                "TABLE_ID": kwargs["id"],
                "ERROR_MSG": str(e),
            }
            logger.info("Error while update table %s" % str(e), extra=extra)
            return Response(
                {"detail": _("Currently, the space limit was reached. Please try again later.")},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

    def _split_table(self, table, analyzed_tables, datasource, child_tables, mergeable=None):
        datasource_dir = os.path.dirname(datasource.files.all()[0].file.path)
        for child_table_key in child_tables:
            analyzed_child_table = analyzed_tables.get(child_table_key, {})
            if analyzed_child_table.total_rows == 0:
                logger.debug(
                    "Skip child table {} for datasource {}".format(child_table_key, datasource),
                    extra={
                        "MESSAGE_ID": "skip_child_table",
                        "TABLE_KEY": child_table_key,
                        "DATASOURCE_ID": str(datasource.id),
                        "MODEL": datasource.__class__.__name__,
                    },
                )
                continue

            parent_arrays = analyzed_tables[child_table_key].parent.arrays
            child_path = analyzed_tables[child_table_key].path[0]
            array_size = parent_arrays[child_path]
            if mergeable is None or mergeable is True:
                mergeable = False if array_size >= TABLE_THRESHOLD else True
            child_table = Table.objects.create(
                name=child_table_key, parent=analyzed_tables[child_table_key].parent.name, mergeable=mergeable
            )
            table.array_tables.add(child_table)
            preview_path = f"{datasource_dir}/{child_table_key}_combined.csv"
            store_preview_csv(COLUMNS, PREVIEW_ROWS, analyzed_tables[child_table_key], preview_path)
            if analyzed_child_table.child_tables:
                self._split_table(
                    table, analyzed_tables, datasource, analyzed_child_table.child_tables, mergeable=mergeable
                )


class TablePreviewViewSet(viewsets.GenericViewSet):
    queryset = Table.objects.all()
    http_method_names = ["get", "head", "options", "trace"]

    def list(self, request, url_id=None, upload_id=None, selection_id=None, table_id=None):
        table = Table.objects.get(id=table_id)
        if url_id:
            datasource = Url.objects.get(id=url_id)
        elif upload_id:
            datasource = Upload.objects.get(id=upload_id)
        datasource_dir = os.path.dirname(datasource.files.all()[0].file.path)
        selection = DataSelection.objects.get(id=selection_id)
        try:
            spec = DataPreprocessor.restore(datasource.analyzed_file.path)
            data = []
            if table.split:
                preview_path = f"{datasource_dir}/{table.name}.csv"
                if not os.path.exists(preview_path):
                    store_preview_csv(COLUMNS, PREVIEW_ROWS, spec.tables[table.name], preview_path)
                with open(preview_path) as csvfile:
                    preview = {
                        "name": spec.tables[table.name].name,
                        "id": str(table.id),
                        "preview": csvfile.read(),
                        "heading": table.heading,
                        "should_split": table.should_split,
                        "parent": table.parent,
                        "include": table.include,
                    }
                    if selection.headings_type != selection.OCDS:
                        preview["column_headings"] = table.column_headings
                data.append(preview)
                for child_table in table.array_tables.all():
                    # if not child_table.include:
                    #     continue
                    preview_path = f"{datasource_dir}/{child_table.name}_combined.csv"
                    with open(preview_path) as csvfile:
                        preview = {
                            "name": spec.tables[child_table.name].name,
                            "id": str(child_table.id),
                            "preview": csvfile.read(),
                            "heading": child_table.heading,
                            "mergeable": child_table.mergeable,
                            "should_split": child_table.should_split,
                            "parent": child_table.parent,
                            "include": child_table.include,
                        }
                        if selection.headings_type != selection.OCDS:
                            preview["column_headings"] = child_table.column_headings
                    data.append(preview)
            else:
                preview_path = f"{datasource_dir}/{table.name}_combined.csv"
                if not os.path.exists(preview_path):
                    store_preview_csv(COMBINED_COLUMNS, COMBINED_PREVIEW_ROWS, spec.tables[table.name], preview_path)
                with open(preview_path) as csvfile:
                    preview = {
                        "name": spec.tables[table.name].name,
                        "id": str(table.id),
                        "preview": csvfile.read(),
                        "heading": table.heading,
                        "should_split": table.should_split,
                        "parent": table.parent,
                        "include": table.include,
                    }
                    if selection.headings_type != selection.OCDS:
                        preview["column_headings"] = table.column_headings
                    data.append(preview)
            return Response(data)
        except FileNotFoundError as e:
            extra = {
                "MESSAGE_ID": "get_preview_failed",
                "DATASOURCE_ID": str(datasource.id),
                "TABLE_ID": table_id,
                "ERROR_MSG": str(e),
                "EXPIRED_AT": datasource.expired_at.isoformat(),
            }
            logger.info("Error while get table preview %s" % str(e), extra=extra)
            return Response({"detail": _("Datasource expired.")}, status=status.HTTP_404_NOT_FOUND)
        except OSError as e:
            extra = {
                "MESSAGE_ID": "create_preview_failed",
                "DATASOURCE_ID": str(datasource.id),
                "TABLE_ID": table_id,
                "ERROR_MSG": str(e),
            }
            logger.info("Error while create preview %s" % str(e), extra=extra)
            return Response(
                {"detail": _("Currently, the space limit was reached. Please try again later.")},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )


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

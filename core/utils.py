import csv
import logging
import os
import pathlib
import re
import uuid
from contextlib import contextmanager
from os.path import commonprefix
from urllib.parse import unquote, urlparse
from zipfile import ZipFile

import ijson
from django.conf import settings
from django.utils.translation import activate, get_language
from spoonbill.stats import DataPreprocessor

from core.column_headings import headings
from core.constants import OCDS_LITE_CONFIG

logger = logging.getLogger(__name__)


# DON'T CHANGE ORDER
TABLES_ORDER = (
    "parties",
    "planning",
    "tenders",
    "awards",
    "contracts",
    "documents",
    "milestones",
    "amendments",
)


def instance_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    return "{0}/{1}.json".format(instance.id, uuid.uuid4().hex)


def export_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    selection = instance.dataselection_set.all()[0]
    ds_set = selection.url_set.all() or selection.upload_set.all()
    ds = ds_set[0]
    return "{0}/{1}".format(ds.id, filename.split("/")[-1])


def retrieve_tables(analyzed_data):
    tables = analyzed_data.tables
    available_tables = []
    unavailable_tables = []
    for key in TABLES_ORDER:
        table = tables.get(key, {})
        if table.total_rows == 0:
            unavailable_tables.append(key)
            continue
        arrays = {k: v for k, v in table.arrays.items() if v > 0}
        available_table = {
            "name": table.name,
            "rows": table.total_rows,
            "arrays": arrays,
            "available_data": {
                "columns": {
                    "additional": list(table.additional_columns.keys()),
                    "total": len(table.columns.keys()),
                }
            },
        }
        available_cols = 0
        missing_columns_data = []
        for col in table.columns.values():
            if col.hits > 0:
                available_cols += 1
            else:
                missing_columns_data.append(col.id)
        available_table["available_data"]["columns"].update(
            {"available": available_cols, "missing_data": missing_columns_data}
        )
        available_tables.append(available_table)
    return available_tables, unavailable_tables


def store_preview_csv(columns_key, rows_key, table_data, preview_path):
    columns = getattr(table_data, columns_key)
    columns.update(table_data.additional_columns)
    headers = [header for header, col in columns.items() if col.hits > 0]
    if not columns_key.startswith("combined"):
        headers.append("parentTable")
    with open(preview_path, "w", newline="\n") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        rows = getattr(table_data, rows_key)
        writer.writerows(rows)


def transform_to_r(value):
    return value.replace(" ", "_").lower()


def get_column_headings(datasource, tables, table):
    heading_formatters = {
        "en_r_friendly": transform_to_r,
        "es_r_friendly": transform_to_r,
        "en_user_friendly": lambda x: x,
        "es_user_friendly": lambda x: x,
    }
    column_headings = {}
    if datasource.headings_type == "ocds":
        return column_headings
    columns = tables[table.name].columns.keys() if table.split else tables[table.name].combined_columns.keys()
    for col in columns:
        non_index_based = re.sub(r"\d", "*", col)
        column_headings.update({col: heading_formatters[datasource.headings_type](headings.get(non_index_based, col))})
    return column_headings


def set_column_headings(selection, analyzed_file_path):
    current_language_code = get_language()
    spec = DataPreprocessor.restore(analyzed_file_path)
    if selection.headings_type.startswith("es"):
        activate("es")
    for table in selection.tables.all():
        table.column_headings = get_column_headings(selection, spec.tables, table)
        table.save(update_fields=["column_headings"])
        if table.split:
            for a_table in table.array_tables.all():
                a_table.column_headings = get_column_headings(selection, spec.tables, a_table)
                a_table.save(update_fields=["column_headings"])
    activate(current_language_code)


@contextmanager
def internationalization(lang_code="en"):
    current_lang = get_language()
    try:
        activate(lang_code)
        yield
    finally:
        activate(current_lang)


def zip_files(source_dir, zipfile, extension=None):
    with ZipFile(zipfile, "w") as fzip:
        for folder, _, files in os.walk(source_dir):
            for file_ in files:
                if extension and file_.endswith(extension):
                    fzip.write(os.path.join(folder, file_), file_)


def get_only_columns(table, table_config, analyzed_data=None):
    only_columns = []
    only = table_config.get("only", [])
    if not only:
        return only
    columns = (
        analyzed_data.tables[table.name].columns.keys()
        if table.split
        else analyzed_data.tables[table.name].combined_columns.keys()
    )
    for col in columns:
        non_index_based = re.sub(r"\d", "*", col)
        if non_index_based in only:
            only_columns.append(col)
    return only_columns


def get_options_for_table(selections, exclude_tables_list, selection, tables, parent=None, analyzed_data=None):
    for table in tables.all():
        if not table.include:
            exclude_tables_list.append(table.name)
            continue
        else:
            selections[table.name] = {"split": table.split}
        if table.column_headings:
            selections[table.name]["headers"] = table.column_headings
        if table.heading:
            selections[table.name]["name"] = table.heading
        if selection.kind == selection.OCDS_LITE:
            selections[table.name]["pretty_headers"] = True
            lite_table_config = (
                OCDS_LITE_CONFIG["tables"].get(table.name, {})
                if not parent
                else OCDS_LITE_CONFIG["tables"].get(parent.name, {}).get("child_tables", {}).get(table.name, {})
            )
            only = get_only_columns(table, lite_table_config, analyzed_data=analyzed_data)
            if only:
                selections[table.name]["only"] = only
            if "repeat" in lite_table_config:
                selections[table.name]["repeat"] = lite_table_config["repeat"]
        if table.split:
            get_options_for_table(selections, exclude_tables_list, selection, table.array_tables, table, analyzed_data)


def get_flatten_options(selection):
    selections = {}
    exclude_tables_list = []
    spec = None

    if selection.kind == selection.OCDS_LITE:
        datasource = selection.url_set.all() or selection.upload_set.all()
        spec = DataPreprocessor.restore(datasource[0].analyzed_file.path)
    get_options_for_table(selections, exclude_tables_list, selection, selection.tables, analyzed_data=spec)
    options = {"selection": selections}
    if exclude_tables_list:
        options["exclude"] = exclude_tables_list
    return options


def get_protocol(url):
    return urlparse(url).scheme


def dataregistry_path_formatter(path):
    path = pathlib.Path(unquote(urlparse(path).path))
    if str(path).count("/") == 1 and str(path)[0] == "/":
        path = pathlib.Path(str(path).replace("/", ""))
    path = settings.DATAREGISTRY_MEDIA_ROOT / path
    return path


def dataregistry_path_resolver(path):
    path = pathlib.Path(path).resolve()
    return path


def multiple_file_assigner(files, paths):
    for file in files:
        file.file.name = paths[files.index(file)]
        file.save()
    return files

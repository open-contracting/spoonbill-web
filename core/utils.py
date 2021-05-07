import csv
import json
import logging
import os
import re
import uuid
from contextlib import contextmanager
from zipfile import ZipFile

import ijson
from django.utils.translation import activate, get_language

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
    tables = analyzed_data.get("tables", {})
    available_tables = []
    unavailable_tables = []
    for key in TABLES_ORDER:
        table = tables.get(key, {})
        if table.get("total_rows", 0) == 0:
            unavailable_tables.append(key)
            continue
        arrays = {k: v for k, v in table.get("arrays", {}).items() if v > 0}
        available_table = {
            "name": table.get("name"),
            "rows": table.get("total_rows"),
            "arrays": arrays,
            "available_data": {
                "columns": {
                    "additional": list(table.get("additional_columns", {}).keys()),
                    "total": len(table.get("columns", {}).keys()),
                }
            },
        }
        available_cols = 0
        missing_columns_data = []
        for col in table.get("columns", {}).values():
            if col.get("hits", 0) > 0:
                available_cols += 1
            else:
                missing_columns_data.append(col["id"])
        available_table["available_data"]["columns"].update(
            {"available": available_cols, "missing_data": missing_columns_data}
        )
        available_tables.append(available_table)
    return available_tables, unavailable_tables


def store_preview_csv(columns_key, rows_key, table_data, preview_path):
    headers = [header for header, col in table_data[columns_key].items() if col["hits"] > 0]
    if not columns_key.startswith("combined"):
        headers.append("parentTable")
    with open(preview_path, "w", newline="\n") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(table_data[rows_key])


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
    columns = tables[table.name]["columns"].keys() if table.split else tables[table.name]["combined_columns"].keys()
    for col in columns:
        non_index_based = re.sub(r"\d", "*", col)
        column_headings.update({col: heading_formatters[datasource.headings_type](headings.get(non_index_based, col))})
    return column_headings


def set_column_headings(datasource, analyzed_file_path):
    current_language_code = get_language()
    with open(analyzed_file_path) as fd:
        tables = json.loads(fd.read())["tables"]
    if datasource.headings_type.startswith("es"):
        activate("es")
    for table in datasource.tables.all():
        table.column_headings = get_column_headings(datasource, tables, table)
        table.save(update_fields=["column_headings"])
        if table.split:
            for a_table in table.array_tables.all():
                a_table.column_headings = get_column_headings(datasource, tables, a_table)
                a_table.save(update_fields=["column_headings"])
    activate(current_language_code)


def is_release_package(filepath):
    with open(filepath, "rb") as f:
        items = ijson.items(f, "releases.item")
        for item in items:
            if item:
                return True
    return False


def is_record_package(filepath):
    with open(filepath, "rb") as f:
        items = ijson.items(f, "records.item")
        for item in items:
            if item:
                return True
    return False


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


def get_only_columns(table, analyzed_data):
    only_columns = []
    columns = (
        analyzed_data["tables"][table.name]["columns"].keys()
        if table.split
        else analyzed_data["tables"][table.name]["combined_columns"].keys()
    )
    for col in columns:
        non_index_based = re.sub(r"\d", "*", col)
        if non_index_based in OCDS_LITE_CONFIG["tables"][table.name]["only"]:
            only_columns.append(col)
    return only_columns


def get_flatten_options(selection):
    selections = {}
    exclude_tables_list = []

    if selection.kind == selection.OCDS_LITE:
        datasource = selection.url_set.all() or selection.upload_set.all()
        with open(datasource[0].analyzed_file.path) as fd:
            analyzed_data = json.loads(fd.read())
    for table in selection.tables.all():
        if not table.include:
            exclude_tables_list.append(table.name)
            continue
        if selection.kind == selection.OCDS_LITE and table.name in OCDS_LITE_CONFIG["tables"]:
            selections[table.name] = {"split": table.split, "only": get_only_columns(table, analyzed_data)}
        elif selection.kind == selection.OCDS_LITE and table.name not in OCDS_LITE_CONFIG["tables"]:
            extra = {
                "MESSAGE_ID": "skip_table_for_export_config",
                "TABLE_ID": str(table.id),
                "TABLE_NAME": table.name,
                "SELECTION_ID": str(selection.id),
                "SELECTION_KIND": selection.kind,
            }
            logger.info("Skip %s for flatten" % table, extra=extra)
            continue
        else:
            selections[table.name] = {"split": table.split}
        if table.column_headings:
            selections[table.name]["headers"] = table.column_headings
        if table.heading:
            selections[table.name]["name"] = table.heading
        if table.split:
            for a_table in table.array_tables.all():
                if not a_table.include:
                    exclude_tables_list.append(a_table.name)
                    continue
                selections[a_table.name] = {"split": a_table.split}
                if a_table.column_headings:
                    selections[a_table.name]["headers"] = a_table.column_headings
                if a_table.heading:
                    selections[a_table.name]["name"] = a_table.heading
    options = {"selection": selections}
    if exclude_tables_list:
        options["exclude"] = exclude_tables_list
    return options

import csv
import json
import re
import uuid

import ijson
from django.utils.translation import activate, get_language
from spoonbill.common import ROOT_TABLES

from core.column_headings import headings


def instance_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    return "{0}/{1}.json".format(instance.id, uuid.uuid4().hex)


def retrieve_available_tables(analyzed_data):
    tables = analyzed_data.get("tables", {})
    available_tables = []
    for key in ROOT_TABLES:
        if key not in tables:
            continue
        root_table = tables.get(key)
        arrays_count = len([v for v in root_table.get("arrays", {}).values() if v > 0])
        available_table = {
            "name": root_table.get("name"),
            "rows": root_table.get("total_rows"),
            "arrays": {"count": arrays_count},
            "available_data": {
                "columns": {
                    "additional": list(root_table.get("additional_columns", {}).keys()),
                    "total": len(root_table.get("columns", {}).keys()),
                }
            },
        }
        available_cols = 0
        for col in root_table.get("columns", {}).values():
            if col.get("hits", 0) > 0:
                available_cols += 1
        available_table["available_data"]["columns"]["available"] = available_cols
        available_tables.append(available_table)
    return available_tables


def store_preview_csv(columns_key, rows_key, table_data, preview_path):
    headers = set()
    for row in table_data[rows_key]:
        headers |= set(row.keys())
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
    column_headings = []
    if datasource.headings_type == "ocds":
        return column_headings
    columns = tables[table.name]["columns"].keys() if table.split else tables[table.name]["combined_columns"].keys()
    for col in columns:
        non_index_based = re.sub(r"\d", "*", col)
        column_headings.append({col: heading_formatters[datasource.headings_type](headings.get(non_index_based, col))})
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

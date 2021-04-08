import csv
import uuid

from spoonbill.common import ROOT_TABLES


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
    headers = list(table_data[columns_key].keys())
    if "parentTable" not in headers:
        headers.append("parentTable")
    with open(preview_path, "w", newline="\n") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(table_data[rows_key])

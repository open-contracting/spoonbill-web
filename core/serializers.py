from rest_framework import serializers

from core.models import DataSelection, Table, Upload, Url, Validation


class ArrayTablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ("id", "name", "include", "flatten_name")


class TablesSerializer(serializers.ModelSerializer):
    array_tables = ArrayTablesSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        read_only_fields = ("array_tables",)
        fields = "__all__"


class DataSelectionSerializer(serializers.ModelSerializer):
    tables = TablesSerializer(many=True)

    class Meta:
        model = DataSelection
        read_only_fields = ("column_headings",)
        fields = "__all__"


class ValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validation
        fields = ["id", "task_id", "is_valid", "errors"]


class UploadSerializer(serializers.ModelSerializer):
    validation = ValidationSerializer(read_only=True)
    selections = DataSelectionSerializer(read_only=True, many=True)

    class Meta:
        model = Upload
        read_only_fields = (
            "id",
            "analyzed_file",
            "created_at",
            "expired_at",
            "deleted",
            "status",
            "validation",
            "available_tables",
        )
        fields = "__all__"


class UrlSerializer(serializers.ModelSerializer):
    validation = ValidationSerializer(read_only=True)
    selections = DataSelectionSerializer(read_only=True, many=True)

    class Meta:
        model = Url
        read_only_fields = (
            "available_tables",
            "id",
            "created_at",
            "expired_at",
            "deleted",
            "downloaded",
            "status",
            "analyzed_file",
            "file",
            "validation",
            "error",
        )
        fields = "__all__"

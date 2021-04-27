from rest_framework import serializers

from core.models import DataSelection, Flatten, Table, Upload, Url, Validation


class ArrayTablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ("id", "name", "include", "heading")


class TablesSerializer(serializers.ModelSerializer):
    array_tables = ArrayTablesSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        read_only_fields = ("array_tables",)
        fields = ("id", "name", "split", "array_tables", "include", "heading")


class FlattenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flatten
        read_only_fields = ("status", "error", "file")
        fields = "__all__"


class DataSelectionSerializer(serializers.ModelSerializer):
    tables = TablesSerializer(many=True)
    flattens = FlattenSerializer(read_only=True, many=True)

    class Meta:
        model = DataSelection
        read_only_fields = ("headings_type",)
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
            "root_key",
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
            "root_key",
        )
        fields = "__all__"

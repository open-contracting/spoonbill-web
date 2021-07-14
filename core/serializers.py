from django.conf import settings
from rest_framework import serializers

from core.models import DataFile, DataSelection, Flatten, Table, Upload, Url, Validation


class ArrayTablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ("id", "name", "include", "heading")


class DataFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFile
        read_only_fields = ("id", "file")
        fields = "__all__"

    def to_representation(self, obj):
        return settings.MEDIA_URL + obj.file.name


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
    tables = TablesSerializer(many=True, allow_empty=False)
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
    files = DataFileSerializer(read_only=True, many=True)

    class Meta:
        model = Upload
        read_only_fields = (
            "order",
            "analyzed_file",
            "available_tables",
            "created_at",
            "deleted",
            "expired_at",
            "id",
            "root_key",
            "status",
            "unavailable_tables",
            "validation",
            "files",
        )
        fields = "__all__"


class UrlSerializer(serializers.ModelSerializer):
    validation = ValidationSerializer(read_only=True)
    selections = DataSelectionSerializer(read_only=True, many=True)
    files = DataFileSerializer(read_only=True, many=True)

    class Meta:
        model = Url
        read_only_fields = (
            "order",
            "analyzed_file",
            "available_tables",
            "created_at",
            "deleted",
            "downloaded",
            "error",
            "expired_at",
            "files",
            "id",
            "root_key",
            "status",
            "unavailable_tables",
            "validation",
        )
        fields = "__all__"

from rest_framework import serializers

from core.models import Upload, Url, Validation


class ValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validation
        fields = ["id", "task_id", "is_valid", "errors"]


class UploadSerializer(serializers.ModelSerializer):
    validation = ValidationSerializer(read_only=True)

    class Meta:
        model = Upload
        read_only_fields = ("id", "created_at", "expired_at", "deleted", "status")
        fields = "__all__"


class UrlSerializer(serializers.ModelSerializer):
    validation = ValidationSerializer(read_only=True)

    class Meta:
        model = Url
        read_only_fields = ("id", "created_at", "expired_at", "deleted", "downloaded", "status")
        fields = "__all__"

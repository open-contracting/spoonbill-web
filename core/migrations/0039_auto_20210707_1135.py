# Generated by Django 3.2.3 on 2021-07-07 11:35

import uuid

import django.contrib.postgres.fields
import django.core.files.storage
from django.db import migrations, models

import core.utils
import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0038_auto_20210623_0914"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataFile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        storage=django.core.files.storage.FileSystemStorage(),
                        upload_to=core.utils.instance_directory_path,
                    ),
                ),
            ],
            options={
                "verbose_name": "File",
                "verbose_name_plural": "Files",
                "db_table": "files",
            },
        ),
        migrations.RemoveField(
            model_name="upload",
            name="file",
        ),
        migrations.RemoveField(
            model_name="url",
            name="file",
        ),
        migrations.RemoveField(
            model_name="url",
            name="url",
        ),
        migrations.AddField(
            model_name="url",
            name="urls",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=2048, validators=[core.validators.validate_url_or_path]),
                default=list,
                size=None,
                validators=[core.validators.url_multi_upload_validator],
            ),
        ),
        migrations.AddField(
            model_name="upload",
            name="files",
            field=models.ManyToManyField(blank=True, null=True, to="core.DataFile"),
        ),
        migrations.AddField(
            model_name="url",
            name="files",
            field=models.ManyToManyField(blank=True, null=True, to="core.DataFile"),
        ),
    ]
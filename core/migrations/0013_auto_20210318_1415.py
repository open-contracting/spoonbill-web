# Generated by Django 3.1.7 on 2021-03-18 14:15

import django.core.files.storage
from django.db import migrations, models

import core.utils


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_auto_20210318_1411"),
    ]

    operations = [
        migrations.AlterField(
            model_name="upload",
            name="file",
            field=models.FileField(
                storage=django.core.files.storage.FileSystemStorage(), upload_to=core.utils.instance_directory_path
            ),
        ),
        migrations.AlterField(
            model_name="url",
            name="analyzed_data_file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=django.core.files.storage.FileSystemStorage(),
                upload_to=core.utils.instance_directory_path,
            ),
        ),
        migrations.AlterField(
            model_name="url",
            name="data_file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=django.core.files.storage.FileSystemStorage(),
                upload_to=core.utils.instance_directory_path,
            ),
        ),
    ]

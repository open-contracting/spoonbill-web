# Generated by Django 3.2 on 2021-04-07 10:31

import django.core.files.storage
from django.db import migrations, models

import core.utils


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0020_auto_20210405_0538"),
    ]

    operations = [
        migrations.AddField(
            model_name="upload",
            name="analyzed_file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=django.core.files.storage.FileSystemStorage(),
                upload_to=core.utils.instance_directory_path,
            ),
        ),
    ]

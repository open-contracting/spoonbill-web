# Generated by Django 3.2.3 on 2021-08-27 07:32

from django.db import migrations, models

import spoonbill_web.file_storage
import spoonbill_web.utils


class Migration(migrations.Migration):
    dependencies = [
        ("spoonbill_web", "0040_auto_20210713_1235"),
    ]

    operations = [
        migrations.AddField(
            model_name="url",
            name="author",
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name="datafile",
            name="file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=spoonbill_web.file_storage.MediaAndDataregistryFS(),
                upload_to=spoonbill_web.utils.instance_directory_path,
            ),
        ),
        migrations.AlterField(
            model_name="flatten",
            name="file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=spoonbill_web.file_storage.MediaAndDataregistryFS(),
                upload_to=spoonbill_web.utils.export_directory_path,
            ),
        ),
        migrations.AlterField(
            model_name="upload",
            name="analyzed_file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=spoonbill_web.file_storage.MediaAndDataregistryFS(),
                upload_to=spoonbill_web.utils.instance_directory_path,
            ),
        ),
        migrations.AlterField(
            model_name="url",
            name="analyzed_file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=spoonbill_web.file_storage.MediaAndDataregistryFS(),
                upload_to=spoonbill_web.utils.instance_directory_path,
            ),
        ),
    ]
# Generated by Django 3.2 on 2021-04-29 12:27

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0033_alter_table_heading"),
    ]

    operations = [
        migrations.AddField(
            model_name="upload",
            name="unavailable_tables",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=50), default=list, size=None
            ),
        ),
        migrations.AddField(
            model_name="url",
            name="unavailable_tables",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=50), default=list, size=None
            ),
        ),
    ]

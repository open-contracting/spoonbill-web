# Generated by Django 3.2 on 2021-04-16 09:27

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0027_auto_20210416_0927"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="column_headings",
            field=models.JSONField(
                blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True
            ),
        ),
    ]

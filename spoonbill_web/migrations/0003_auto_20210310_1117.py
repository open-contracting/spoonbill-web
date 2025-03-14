# Generated by Django 3.1.7 on 2021-03-10 11:17

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spoonbill_web", "0002_auto_20210310_1049"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flattenrequest",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="flattenrequest",
            name="id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]

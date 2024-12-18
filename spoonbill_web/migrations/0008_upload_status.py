# Generated by Django 3.1.7 on 2021-03-17 09:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spoonbill_web", "0007_auto_20210311_1308"),
    ]

    operations = [
        migrations.AddField(
            model_name="upload",
            name="status",
            field=models.CharField(
                choices=[("queued.validation", "Queued validation"), ("validation", "Validation")],
                default="queued.validation",
                max_length=32,
            ),
        ),
    ]

# Generated by Django 3.2 on 2021-04-16 11:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spoonbill_web", "0028_table_column_headings"),
    ]

    operations = [
        migrations.AddField(
            model_name="upload",
            name="root_key",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="url",
            name="root_key",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]

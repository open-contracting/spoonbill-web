# Generated by Django 3.2.3 on 2021-09-28 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0043_table_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="mergeable",
            field=models.BooleanField(default=False),
        ),
    ]
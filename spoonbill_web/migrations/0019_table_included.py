# Generated by Django 3.1.7 on 2021-03-31 07:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spoonbill_web", "0018_table_splitted"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="included",
            field=models.BooleanField(default=True),
        ),
    ]
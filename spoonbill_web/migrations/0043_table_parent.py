# Generated by Django 3.2.3 on 2021-09-24 10:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spoonbill_web", "0042_alter_url_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="parent",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]

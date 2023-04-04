# Generated by Django 3.2.12 on 2022-04-05 21:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0046_alter_url_country"),
    ]

    operations = [
        migrations.AlterField(
            model_name="upload",
            name="files",
            field=models.ManyToManyField(blank=True, to="core.DataFile"),
        ),
        migrations.AlterField(
            model_name="url",
            name="files",
            field=models.ManyToManyField(blank=True, to="core.DataFile"),
        ),
    ]

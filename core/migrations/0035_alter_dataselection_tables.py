# Generated by Django 3.2 on 2021-05-05 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0034_auto_20210429_1227"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dataselection",
            name="tables",
            field=models.ManyToManyField(to="core.Table"),
        ),
    ]
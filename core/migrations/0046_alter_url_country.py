# Generated by Django 3.2.3 on 2021-09-30 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0045_table_should_split"),
    ]

    operations = [
        migrations.AlterField(
            model_name="url",
            name="country",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
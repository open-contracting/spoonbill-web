# Generated by Django 4.2.4 on 2023-08-17 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_auto_20220405_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='array_tables',
            field=models.ManyToManyField(blank=True, to='core.table'),
        ),
    ]

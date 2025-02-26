# Generated by Django 3.1.7 on 2021-03-10 10:49

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spoonbill_web", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="flattenrequest",
            name="created_at",
            field=models.DateTimeField(auto_created=True, auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="flattenrequest",
            name="expired_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

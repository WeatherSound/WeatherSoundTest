# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20170808_0116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weather',
            name='time_saved',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 07:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20170804_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='music',
            name='img_music',
            field=models.CharField(max_length=256),
        ),
    ]

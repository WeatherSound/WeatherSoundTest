# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-08 07:06
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_auto_20170808_0248'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='weather',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]
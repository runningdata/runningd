# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-12 11:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metamap', '0021_auto_20161212_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='sqoopmysql2hive',
            name='settings',
            field=models.TextField(null=True),
        ),
    ]

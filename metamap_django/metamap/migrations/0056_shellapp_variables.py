# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-06-22 06:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metamap', '0055_shellapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='shellapp',
            name='variables',
            field=models.CharField(default=b'', max_length=2000),
        ),
    ]

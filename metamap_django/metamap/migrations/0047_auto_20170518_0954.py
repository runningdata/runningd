# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-05-18 09:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metamap', '0046_auto_20170518_0710'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ETLBlood',
            new_name='ExecBlood',
        ),
    ]
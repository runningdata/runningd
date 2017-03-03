# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
定义一些自定义的字段类型，方便于数据库与python之间的转换
created by will 
'''
from datetime import datetime
from django.db import models


class Long2Date(models.Field):
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return datetime.utcfromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")

class WillFileField(models.FileField):
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return datetime.utcfromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
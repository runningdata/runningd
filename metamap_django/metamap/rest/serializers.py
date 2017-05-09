# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
import pytz
from django.utils import six
from rest_framework import serializers, ISO_8601
from rest_framework.settings import api_settings

from metamap.models import ETL, AnaETL, Exports, WillDependencyTask, BIUser, Meta, SqoopHive2Mysql, SqoopMysql2Hive, \
    SourceApp, JarApp
from will_common.serializers import WillDateTimeField


class ETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ETL
        fields = ('name', 'valid', 'id')


class SourceAppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SourceApp
        fields = ('name', 'id')


class JarAppSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JarApp
        fields = ('name', 'id')


class SqoopHive2MysqlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SqoopHive2Mysql
        fields = ('name', 'id')


class SqoopMysql2HiveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SqoopMysql2Hive
        fields = ('name', 'id')


class AnaETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AnaETL
        fields = ('name', 'valid', 'id')


class WillTaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WillDependencyTask
        fields = ('name', 'valid', 'id')


class ExportsSerializer(serializers.HyperlinkedModelSerializer):
    start_time = WillDateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = WillDateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Exports
        fields = ('file_loc', 'start_time', 'end_time')


class MetaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Meta
        fields = ('meta', 'db', 'id', 'ctime')

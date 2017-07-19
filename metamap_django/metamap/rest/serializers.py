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
    SourceApp, JarApp, ExecObj, ExecutionsV2
from will_common.serializers import WillDateTimeField
from will_common.templatetags import etlutils


class ETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ETL
        fields = ('name', 'valid', 'id')


class ExecObjSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExecObj
        fields = ('name', 'id', 'type')


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
        # model = AnaETL
        model = ExecObj
        fields = ('name', 'id')


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


class ExecutionsV2Serializer(serializers.HyperlinkedModelSerializer):
    start_time = WillDateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = WillDateTimeField(format='%Y-%m-%d %H:%M:%S')
    file_loc = serializers.SerializerMethodField()
    file_status = serializers.SerializerMethodField()

    class Meta:
        model = ExecutionsV2
        fields = ('file_loc', 'start_time', 'end_time', 'file_status')

    def get_file_loc(self, obj):
        return obj.log_location.replace('/var/azkaban-metamap/', '').replace('.error', '')

    def get_file_status(self, obj):
        return etlutils.readable_status(obj.status)


class MetaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Meta
        fields = ('meta', 'db', 'id', 'ctime')

# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from rest_framework import serializers

from metamap.models import ETL, AnaETL, Exports, WillDependencyTask, BIUser, Meta, SqoopHive2Mysql, SqoopMysql2Hive, \
    SourceApp, JarApp


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


class BIUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BIUser
        fields = ('username',)


class AnaETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AnaETL
        fields = ('name', 'valid', 'id')


class WillTaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WillDependencyTask
        fields = ('name', 'valid', 'id')


class ExportsSerializer(serializers.HyperlinkedModelSerializer):
    task = WillTaskSerializer(required=True)
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Exports
        fields = ('file_loc', 'start_time', 'end_time')


class MetaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Meta
        fields = ('meta', 'db', 'id', 'ctime')

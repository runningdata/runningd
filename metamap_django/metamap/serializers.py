# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from rest_framework import serializers

from metamap.models import ETL, AnaETL, Exports, WillDependencyTask


class ETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ETL
        fields = ('tblName', 'valid', 'id')

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
    class Meta:
        model = Exports
        fields = ('file_loc', 'start_time', 'end_time', 'command', 'task')
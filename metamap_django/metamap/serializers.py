# !/usr/bin/env python
# -*- coding: utf-8 -*
'''
created by will 
'''
from rest_framework import serializers

from metamap.models import ETL, AnaETL


class ETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ETL
        fields = ('tblName', 'valid', 'id')

class AnaETLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AnaETL
        fields = ('name', 'valid', 'id')